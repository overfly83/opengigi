@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Send a message to the agent and stream the response using Server-Sent Events.

    The response is a stream of SSE events with the following types:
    - message_delta: Partial message content
    - message_complete: Final message content
    - tool_call: Tool call information
    - tool_result: Tool execution result
    - error: Error information
    - [DONE]: End of stream marker
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return StreamingResponse(
        _stream_chat_response(request.message, request.thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

async def _stream_chat_response(
    message: str,
    thread_id: str
) -> AsyncGenerator[str, None]:
    """Stream chat response using Server-Sent Events.

    Uses async streaming (astream) to properly support MCP tools which
    are async-only (StructuredTool with coroutine but no sync func).
    """
    logger.debug(f"[Stream] Starting async stream for thread={thread_id}, message={message[:100]}...")

    if agent is None:
        error_event = {'type': 'error', 'message': 'Agent not initialized'}
        logger.error(f"[SSE→Client] type=error | Agent not initialized")
        yield f"data: {json.dumps(error_event)}\n\n"
        return

    try:
        # Track message IDs we've already sent (using LangChain message ID)
        sent_message_ids = set()
        accumulated_content = ""
        chunk_count = 0
        is_first_chunk = True
        initial_message_ids = set()  # Store IDs of messages in first chunk (historical)

        # Use async streaming to support MCP tools (which are async-only)
        async for chunk in agent.astream(message, thread_id=thread_id):
            chunk_count += 1
            logger.debug(f"[Stream] Chunk #{chunk_count} received, keys: {list(chunk.keys())}")

            for node_name, node_output in chunk.items():
                logger.debug(f"[Stream] Processing node: {node_name}, output type: {type(node_output).__name__}")

                if isinstance(node_output, dict) and "messages" in node_output:
                    # Handle messages from the chunk
                    messages_value = node_output["messages"]

                    # Extract messages (handle Overwrite wrapper)
                    if hasattr(messages_value, 'value'):
                        messages_value = messages_value.value
                    if not isinstance(messages_value, list):
                        messages_value = [messages_value] if messages_value else []

                    logger.debug(f"[Stream] Processing {len(messages_value)} message(s) from chunk (first_chunk={is_first_chunk})")

                    # On first chunk, collect all message IDs as "historical"
                    # These are messages from the checkpoint/history
                    if is_first_chunk:
                        for msg in messages_value:
                            msg_id = getattr(msg, 'id', None) or str(id(msg))
                            initial_message_ids.add(msg_id)
                            logger.debug(f"[Stream] Marking as historical: msg_id={msg_id}, type={type(msg).__name__}")
                        is_first_chunk = False
                        continue  # Skip processing first chunk - it's all history

                    for msg in messages_value:
                        # Get message ID - prefer LangChain's message ID
                        msg_id = getattr(msg, 'id', None) or str(id(msg))

                        # Skip if already sent
                        if msg_id in sent_message_ids:
                            logger.debug(f"[Stream] Skipping duplicate message id={msg_id}")
                            continue

                        # Skip if it's a historical message from the first chunk
                        if msg_id in initial_message_ids:
                            logger.debug(f"[Stream] Skipping historical message id={msg_id}")
                            continue

                        sent_message_ids.add(msg_id)

                        msg_type = type(msg).__name__
                        content = _get_text_content(getattr(msg, "content", ""))

                        logger.debug(f"[Stream] Message type={msg_type}, id={msg_id}, content_len={len(content)}, has_tool_calls={hasattr(msg, 'tool_calls') and bool(msg.tool_calls)}")

                        # Skip HumanMessage - the frontend already shows user messages
                        if msg_type == "HumanMessage":
                            logger.debug(f"[Stream] Skipping HumanMessage (already shown in frontend)")
                            continue

                        if msg_type == "AIMessage" and content:
                            # Send message delta
                            event_data = {'type': 'message_delta', 'content': content}
                            yield _log_sse_event('message_delta', event_data)
                            accumulated_content = content

                            # Check for tool calls
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tc in msg.tool_calls:
                                    tool_event = {
                                        'type': 'tool_call',
                                        'tool_call': {
                                            'id': tc.get('id', ''),
                                            'name': tc.get('name', ''),
                                            'arguments': tc.get('args', {})
                                        }
                                    }
                                    yield _log_sse_event('tool_call', tool_event)

                        elif msg_type == "ToolMessage" and content:
                            tool_result_event = {
                                'type': 'tool_result',
                                'tool_result': {
                                    'name': getattr(msg, 'name', 'tool'),
                                    'content': content[:500]
                                }
                            }
                            yield _log_sse_event('tool_result', tool_result_event)

        # Send completion event
        complete_event = {'type': 'message_complete', 'content': accumulated_content}
        yield _log_sse_event('message_complete', complete_event)

        logger.debug(f"[SSE→Client] [DONE] - Stream completed, total chunks: {chunk_count}")
        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error(f"Streaming error: {e}", exc_info=True)
        error_event = {'type': 'error', 'message': str(e)}
        yield _log_sse_event('error', error_event)



const sendMessageStreaming = useCallback(
    async (content: string) => {
      setIsStreaming(true);

      // Create a placeholder message for streaming
      const assistantMessageId = generateId();
      const placeholderMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, placeholderMessage]);

      try {
        // Use fetch with ReadableStream for SSE
        const response = await fetch(`${API_BASE}/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: content,
            thread_id: threadId,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let accumulatedContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete SSE events from buffer
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);

              if (data === '[DONE]') {
                // Streaming complete
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, isStreaming: false }
                      : msg
                  )
                );
                continue;
              }

              const event = parseSSEData<{
                type: SSEEventType;
                content?: string;
                message?: string;
                tool_call?: unknown;
                tool_result?: unknown;
              }>(data);

              if (!event) continue;

              switch (event.type) {
                case 'message_delta':
                  if (event.content) {
                    accumulatedContent += event.content;
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === assistantMessageId
                          ? { ...msg, content: accumulatedContent }
                          : msg
                      )
                    );
                  }
                  break;

                case 'message_complete':
                  if (event.content) {
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === assistantMessageId
                          ? { ...msg, content: event.content!, isStreaming: false }
                          : msg
                      )
                    );
                  }
                  break;

                case 'tool_call':
                  // Add tool call message
                  const toolCallMsg: Message = {
                    id: generateId(),
                    role: 'tool',
                    content: `Calling tool: ${JSON.stringify(event.tool_call)}`,
                    timestamp: new Date(),
                  };
                  setMessages((prev) => {
                    // Insert before the streaming message
                    const streamingIndex = prev.findIndex(
                      (m) => m.id === assistantMessageId
                    );
                    if (streamingIndex > 0) {
                      const newMessages = [...prev];
                      newMessages.splice(streamingIndex, 0, toolCallMsg);
                      return newMessages;
                    }
                    return [...prev, toolCallMsg];
                  });
                  break;

                case 'tool_result':
                  // Add tool result message
                  // Extract the content from tool_result (which has {name, content} structure from SSE)
                  const rawToolResult = event.tool_result as { name?: string; content?: string } | undefined;
                  const toolResultContent = rawToolResult?.content || JSON.stringify(event.tool_result);
                  const toolResultMsg: Message = {
                    id: generateId(),
                    role: 'tool',
                    content: toolResultContent,
                    timestamp: new Date(),
                    tool_result: rawToolResult ? {
                      tool_call_id: generateId(), // Generate ID since SSE doesn't provide it
                      name: rawToolResult.name || 'unknown',
                      content: toolResultContent,
                    } : undefined,
                  };
                  setMessages((prev) => {
                    const streamingIndex = prev.findIndex(
                      (m) => m.id === assistantMessageId
                    );
                    if (streamingIndex > 0) {
                      const newMessages = [...prev];
                      newMessages.splice(streamingIndex, 0, toolResultMsg);
                      return newMessages;
                    }
                    return [...prev, toolResultMsg];
                  });
                  break;

                case 'error':
                  throw new Error(event.message || 'Unknown streaming error');

                case 'done':
                  break;
              }
            }
          }
        }

        options.onComplete?.();
      } catch (err) {
        if (err instanceof Error) {
          setError(err);
          options.onError?.(err);

          // Update the streaming message to show error
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: `Error: ${err.message}`,
                    isStreaming: false,
                  }
                : msg
            )
          );
        }
      } finally {
        setIsStreaming(false);
      }
    },
    [threadId, options]
  );
