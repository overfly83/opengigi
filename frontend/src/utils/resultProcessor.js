export class ResultProcessor {
  constructor(app) {
    this.app = app
  }

  processNonStreamingResult(response) {
    const resultData = response.data.data

    if (resultData.messages && Array.isArray(resultData.messages)) {
      this.processNewMessageFormat(resultData.messages)
    } else {
      this.processOldFormat(resultData)
    }
  }

  processNewMessageFormat(messages) {
    let finalAiMessage = null

    for (const message of messages) {
      if (message.type === 'human') {
        this.app.addLog('info', `用户: ${message.content}`)
      } else if (message.type === 'ai') {
        if (message.tool_calls && message.tool_calls.length > 0) {
          this.app.addLog('info', `主Agent (()): ${message.content || '正在调用工具...'}`)
          for (const toolCall of message.tool_calls) {
            if (toolCall.function) {
              const funcName = toolCall.function.name
              let args = {}
              try {
                args = JSON.parse(toolCall.function.arguments)
                if (args.todos) {
                  this.app.todos = args.todos
                }
              } catch (e) {
                args = toolCall.function.arguments
              }
              this.app.addLog('info', `  调用工具: ${funcName} ${JSON.stringify(args)}`)
            }
          }
        } else {
          this.app.addLog('info', `主Agent (()): ${message.content}`)
          finalAiMessage = message
        }
      } else if (message.type === 'tool') {
        this.app.addLog('info', `工具 ${message.name}: ${message.content}`)
      }
    }

    this.app.addLog('info', `=== reflect 阶段 ===`)
    this.app.addLog('info', `结果: ${finalAiMessage ? finalAiMessage.content : '执行完成'}`)
    this.app.addLog('success', '\n=== 目标完成 ===')

    let resultContent = finalAiMessage ? finalAiMessage.content : '执行完成'

    if (resultContent.includes('Returning structured response:')) {
      resultContent = this.extractStructuredResult(resultContent)
    }

    this.app.result = {
      phase: 'reflect',
      result: resultContent.replace(/\\n/g, '\n'),
      is_completed: true,
      todos: this.app.todos
    }
  }

  processOldFormat(resultData) {
    this.app.addLog('info', `=== ${resultData.phase} 阶段 ===`)
    this.app.addLog('info', `结果: ${resultData.result}`)

    if (resultData.is_completed) {
      this.app.addLog('success', '\n=== 目标完成 ===')
    } else {
      this.app.addLog('info', '\n=== 目标进行中 ===')
    }

    if (resultData.todos && resultData.todos.length > 0) {
      this.app.todos = resultData.todos
      this.app.addLog('info', '\n=== 待办事项 ===')
      resultData.todos.forEach(todo => {
        this.app.addLog(todo.status, `  ${todo.content} (${todo.status})`)
      })
    }

    let oldFormatResult = resultData.result
    if (oldFormatResult.includes('Returning structured response:')) {
      oldFormatResult = this.extractStructuredResult(oldFormatResult)
    }

    this.app.result = {
      ...resultData,
      result: oldFormatResult.replace(/\\n/g, '\n')
    }
  }

  extractStructuredResult(content) {
    if (content.includes('Returning structured response:')) {
      const structuredStart = content.indexOf('Returning structured response:') + 'Returning structured response:'.length
      let structuredContent = content.substring(structuredStart).trim()

      if (structuredContent.includes('result=')) {
        const resultStart = structuredContent.indexOf('result=') + 'result='.length
        let resultEnd = structuredContent.indexOf(' is_simple_and_unrelevant=')
        if (resultEnd === -1) {
          resultEnd = structuredContent.indexOf(' is_completed=')
        }
        if (resultEnd !== -1) {
          let resultStr = structuredContent.substring(resultStart, resultEnd).trim()
          if (resultStr.startsWith('\'')) {
            resultStr = resultStr.substring(1)
          }
          if (resultStr.endsWith('\'')) {
            resultStr = resultStr.substring(0, resultStr.length - 1)
          }
          return resultStr
        }
      }
    }
    return content
  }
}
