export class ChunkCacheManager {
  constructor(app) {
    this.app = app
    this.cache = {
      currentTaskIndex: -1,
      cachedChunks: [],
      taskKeywords: [],
      lastTodoUpdate: null
    }
  }

  initialize(todos) {
    this.cache.currentTaskIndex = -1
    this.cache.cachedChunks = []
    this.cache.taskKeywords = []
    this.cache.lastTodoUpdate = JSON.parse(JSON.stringify(todos))

    todos.forEach((todo, index) => {
      this.cache.taskKeywords.push({
        index: index,
        keywords: this.extractKeywords(todo.content)
      })
    })

    console.log('Chunk cache initialized with', this.cache.taskKeywords.length, 'tasks')
  }

  extractKeywords(text) {
    const keywords = []
    const patterns = [
      /搜索\s*([^\s，。！？]+)/,
      /分析\s*([^\s，。！？]+)/,
      /评估\s*([^\s，。！？]+)/,
      /完成\s*([^\s，。！？]+)/,
      /总结\s*([^\s，。！？]+)/,
      /([^\s，。！？]+)\s*数据/,
      /([^\s，。！？]+)\s*分析/,
      /([^\s，。！？]+)\s*报告/
    ]

    patterns.forEach(pattern => {
      const match = text.match(pattern)
      if (match) {
        keywords.push(match[1])
      }
    })

    if (keywords.length === 0) {
      keywords.push(text)
    }

    return keywords
  }

  cacheChunk(chunk) {
    this.cache.cachedChunks.push(chunk)
  }

  detectTaskFromChunk(chunk) {
    let bestMatchIndex = -1
    let bestMatchScore = 0

    this.cache.taskKeywords.forEach(task => {
      let score = 0
      task.keywords.forEach(keyword => {
        if (chunk.includes(keyword)) {
          score += 1
        }
      })

      if (score > bestMatchScore) {
        bestMatchScore = score
        bestMatchIndex = task.index
      }
    })

    if (bestMatchScore > 0) {
      return bestMatchIndex
    }

    return -1
  }

  flushCachedChunks(taskIndex) {
    if (this.cache.cachedChunks.length > 0) {
      const taskContent = this.cache.cachedChunks.join('')

      if (taskIndex >= 0 && this.app.todos[taskIndex]) {
        this.app.addLog('info', `--- 任务 ${taskIndex + 1}: ${this.app.todos[taskIndex].content} ---`)
      }

      const processedContent = this.app.processContentForTodos(taskContent)
      if (processedContent) {
        this.app.addLog('info', processedContent)
      }

      this.cache.cachedChunks = []
      
      // 重置 currentStream，以便后续内容在新的容器中显示
      this.app.currentStream = null
    }
  }

  reset() {
    this.cache.currentTaskIndex = -1
    this.cache.cachedChunks = []
    this.cache.taskKeywords = []
    this.cache.lastTodoUpdate = null
  }
}
