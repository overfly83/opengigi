<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl p-6 max-h-[80vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800 dark:text-white">Help & Documentation</h3>
        <button class="text-gray-400 hover:text-gray-600 dark:text-gray-300 dark:hover:text-white" @click="close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="border-b border-gray-200 dark:border-gray-700 mb-4">
        <ul class="flex flex-wrap -mb-px text-sm font-medium text-center" id="helpTab" role="tablist">
          <li class="mr-2" role="presentation">
            <button 
              @click="activeTab = 'overview'"
              :class="['inline-block p-4 border-b-2 rounded-t-lg', activeTab === 'overview' ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-300' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300']"
              id="overview-tab"
              data-tab-target="#overview"
              type="button"
              role="tab"
              aria-controls="overview"
              aria-selected="true"
            >
              <i class="fas fa-info-circle mr-2"></i>Overview
            </button>
          </li>
          <li class="mr-2" role="presentation">
            <button 
              @click="activeTab = 'tutorial'"
              :class="['inline-block p-4 border-b-2 rounded-t-lg', activeTab === 'tutorial' ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-300' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300']"
              id="tutorial-tab"
              data-tab-target="#tutorial"
              type="button"
              role="tab"
              aria-controls="tutorial"
              aria-selected="false"
            >
              <i class="fas fa-graduation-cap mr-2"></i>Tutorial
            </button>
          </li>
          <li class="mr-2" role="presentation">
            <button 
              @click="activeTab = 'faq'"
              :class="['inline-block p-4 border-b-2 rounded-t-lg', activeTab === 'faq' ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-300' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300']"
              id="faq-tab"
              data-tab-target="#faq"
              type="button"
              role="tab"
              aria-controls="faq"
              aria-selected="false"
            >
              <i class="fas fa-question-circle mr-2"></i>FAQ
            </button>
          </li>
          <li class="mr-2" role="presentation">
            <button 
              @click="activeTab = 'docs'"
              :class="['inline-block p-4 border-b-2 rounded-t-lg', activeTab === 'docs' ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-300' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300']"
              id="docs-tab"
              data-tab-target="#docs"
              type="button"
              role="tab"
              aria-controls="docs"
              aria-selected="false"
            >
              <i class="fas fa-book mr-2"></i>Documentation
            </button>
          </li>
          <li role="presentation">
            <button 
              @click="activeTab = 'support'"
              :class="['inline-block p-4 border-b-2 rounded-t-lg', activeTab === 'support' ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-300' : 'border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300']"
              id="support-tab"
              data-tab-target="#support"
              type="button"
              role="tab"
              aria-controls="support"
              aria-selected="false"
            >
              <i class="fas fa-headset mr-2"></i>Support
            </button>
          </li>
        </ul>
      </div>
      
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="p-4">
          <h4 class="text-md font-semibold text-gray-800 dark:text-white mb-3">About Autonomous Decision Agent</h4>
          <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
            The Autonomous Decision Agent is an intelligent system designed to help you achieve your goals by breaking them down into actionable tasks and executing them autonomously.
          </p>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div class="flex items-center mb-2">
                <i class="fas fa-bullseye text-blue-500 mr-2"></i>
                <h5 class="font-medium text-gray-800 dark:text-white">Set Goals</h5>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-300">Define your objectives and let the agent create a plan to achieve them.</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div class="flex items-center mb-2">
                <i class="fas fa-tasks text-blue-500 mr-2"></i>
                <h5 class="font-medium text-gray-800 dark:text-white">Task Management</h5>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-300">Track and monitor the progress of tasks as they are executed.</p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <div class="flex items-center mb-2">
                <i class="fas fa-flag-checkered text-blue-500 mr-2"></i>
                <h5 class="font-medium text-gray-800 dark:text-white">Execution Results</h5>
              </div>
              <p class="text-xs text-gray-600 dark:text-gray-300">View detailed results and insights from the agent's execution.</p>
            </div>
          </div>
          
          <div class="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
            <h5 class="font-medium text-blue-800 dark:text-blue-300 mb-2">Quick Start</h5>
            <ol class="list-decimal list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
              <li>Enter your goal in the "Set Goal" field</li>
              <li>Select your preferred execution mode (Streaming or Non-Streaming)</li>
              <li>Click "Start Execution" to begin</li>
              <li>Monitor the progress in the "Task List" and "Execution Process" sections</li>
              <li>Review the results in the "Execution Result" section</li>
            </ol>
          </div>
        </div>
      </div>
      
      <!-- Tutorial Tab -->
      <div v-if="activeTab === 'tutorial'" class="tab-content">
        <div class="p-4">
          <h4 class="text-md font-semibold text-gray-800 dark:text-white mb-3">Interactive Tutorial</h4>
          
          <div class="space-y-6">
            <div class="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
              <div class="flex items-center mb-2">
                <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3">1</div>
                <h5 class="font-medium text-gray-800 dark:text-white">Setting Your Goal</h5>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-300 ml-11">
                In the "Set Goal" section, enter a clear and specific objective that you want the agent to accomplish. The more detailed your goal, the better the agent can plan and execute tasks.
              </p>
            </div>
            
            <div class="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
              <div class="flex items-center mb-2">
                <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3">2</div>
                <h5 class="font-medium text-gray-800 dark:text-white">Choosing Execution Mode</h5>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-300 ml-11">
                Select between "Streaming Mode" and "Non-Streaming Mode":
              </p>
              <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 ml-11 mt-2 space-y-1">
                <li><strong>Streaming Mode:</strong> View execution process in real-time</li>
                <li><strong>Non-Streaming Mode:</strong> View complete execution result at once</li>
              </ul>
            </div>
            
            <div class="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
              <div class="flex items-center mb-2">
                <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3">3</div>
                <h5 class="font-medium text-gray-800 dark:text-white">Monitoring Execution</h5>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-300 ml-11">
                Once you start execution, you can monitor the progress in the "Task List" section, which shows each task's status. The "Execution Process" section displays detailed logs of the agent's activities.
              </p>
            </div>
            
            <div class="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
              <div class="flex items-center mb-2">
                <div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3">4</div>
                <h5 class="font-medium text-gray-800 dark:text-white">Reviewing Results</h5>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-300 ml-11">
                After execution completes, the "Execution Result" section will display the final output. This includes the agent's analysis and any structured response generated for your goal.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- FAQ Tab -->
      <div v-if="activeTab === 'faq'" class="tab-content">
        <div class="p-4">
          <h4 class="text-md font-semibold text-gray-800 dark:text-white mb-3">Frequently Asked Questions</h4>
          
          <div class="space-y-4">
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg">
              <button 
                @click="toggleFaq(1)"
                class="w-full flex justify-between items-center p-4 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-t-lg"
              >
                <span class="font-medium text-gray-800 dark:text-white">What is the difference between Streaming and Non-Streaming mode?</span>
                <i :class="['fas', faqOpen[1] ? 'fa-chevron-up' : 'fa-chevron-down', 'text-gray-400']"></i>
              </button>
              <div v-if="faqOpen[1]" class="p-4 border-t border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-600 dark:text-gray-300">
                  Streaming mode displays the execution process in real-time, showing each step as it happens. Non-Streaming mode waits until the entire execution is complete before displaying the final result.
                </p>
              </div>
            </div>
            
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg">
              <button 
                @click="toggleFaq(2)"
                class="w-full flex justify-between items-center p-4 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-t-lg"
              >
                <span class="font-medium text-gray-800 dark:text-white">How does the agent break down my goal into tasks?</span>
                <i :class="['fas', faqOpen[2] ? 'fa-chevron-up' : 'fa-chevron-down', 'text-gray-400']"></i>
              </button>
              <div v-if="faqOpen[2]" class="p-4 border-t border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-600 dark:text-gray-300">
                  The agent uses advanced AI to analyze your goal and break it down into smaller, manageable tasks. It considers the complexity of the goal and creates a logical sequence of steps to achieve it.
                </p>
              </div>
            </div>
            
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg">
              <button 
                @click="toggleFaq(3)"
                class="w-full flex justify-between items-center p-4 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-t-lg"
              >
                <span class="font-medium text-gray-800 dark:text-white">Can I interrupt the execution process?</span>
                <i :class="['fas', faqOpen[3] ? 'fa-chevron-up' : 'fa-chevron-down', 'text-gray-400']"></i>
              </button>
              <div v-if="faqOpen[3]" class="p-4 border-t border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-600 dark:text-gray-300">
                  Currently, the agent does not support interrupting an ongoing execution. Once started, it will run to completion. If you need to stop it, you can refresh the page.
                </p>
              </div>
            </div>
            
            <div class="border border-gray-200 dark:border-gray-700 rounded-lg">
              <button 
                @click="toggleFaq(4)"
                class="w-full flex justify-between items-center p-4 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-t-lg"
              >
                <span class="font-medium text-gray-800 dark:text-white">How is my data handled?</span>
                <i :class="['fas', faqOpen[4] ? 'fa-chevron-up' : 'fa-chevron-down', 'text-gray-400']"></i>
              </button>
              <div v-if="faqOpen[4]" class="p-4 border-t border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-600 dark:text-gray-300">
                  The agent processes your data locally and does not store it permanently. Any historical data is stored in your browser's local storage and can be cleared at any time.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Documentation Tab -->
      <div v-if="activeTab === 'docs'" class="tab-content">
        <div class="p-4">
          <h4 class="text-md font-semibold text-gray-800 dark:text-white mb-3">Component Documentation</h4>
          
          <div class="space-y-6">
            <div>
              <h5 class="font-medium text-gray-800 dark:text-white mb-2">Set Goal</h5>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                The Set Goal component allows you to enter your objective for the agent. It includes:
              </p>
              <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>Textarea for entering your goal</li>
                <li>Execution mode selection (Streaming/Non-Streaming)</li>
                <li>Start Execution button</li>
              </ul>
            </div>
            
            <div>
              <h5 class="font-medium text-gray-800 dark:text-white mb-2">Task List</h5>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                The Task List component displays the tasks generated by the agent. It includes:
              </p>
              <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>Task status indicators (Pending, In Progress, Completed, Skipped)</li>
                <li>Task priority levels (High, Medium, Low)</li>
                <li>Status filter dropdown</li>
              </ul>
            </div>
            
            <div>
              <h5 class="font-medium text-gray-800 dark:text-white mb-2">Execution Process</h5>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                The Execution Process component shows detailed logs of the agent's activities. It includes:
              </p>
              <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>Timestamped log entries</li>
                <li>Task execution details</li>
                <li>Error messages (if any)</li>
              </ul>
            </div>
            
            <div>
              <h5 class="font-medium text-gray-800 dark:text-white mb-2">Execution Result</h5>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                The Execution Result component displays the final output from the agent. It includes:
              </p>
              <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>Structured response data</li>
                <li>Formatted result output</li>
                <li>Task completion summary</li>
              </ul>
            </div>
            
            <div>
              <h5 class="font-medium text-gray-800 dark:text-white mb-2">Memory Module</h5>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-2">
                The Memory Module is a feature in development that will store and retrieve the agent's historical execution records. It includes:
              </p>
              <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>Historical Records</li>
                <li>Learning Capability</li>
                <li>Knowledge Graph</li>
                <li>Pattern Recognition</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Support Tab -->
      <div v-if="activeTab === 'support'" class="tab-content">
        <div class="p-4">
          <h4 class="text-md font-semibold text-gray-800 dark:text-white mb-3">Contact Support</h4>
          
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-4">
            <h5 class="font-medium text-gray-800 dark:text-white mb-2">Get Help</h5>
            <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">
              If you need assistance or have questions about the Autonomous Decision Agent, please use one of the following methods to contact support:
            </p>
            
            <div class="space-y-3">
              <div class="flex items-center">
                <i class="fas fa-envelope text-blue-500 mr-3"></i>
                <span class="text-sm text-gray-600 dark:text-gray-300">support@autonomous-agent.com</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-github text-blue-500 mr-3"></i>
                <span class="text-sm text-gray-600 dark:text-gray-300">github.com/autonomous-agent</span>
              </div>
              <div class="flex items-center">
                <i class="fas fa-discord text-blue-500 mr-3"></i>
                <span class="text-sm text-gray-600 dark:text-gray-300">Autonomous Agent Discord</span>
              </div>
            </div>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h5 class="font-medium text-gray-800 dark:text-white mb-2">Version Information</h5>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-gray-600 dark:text-gray-300">Current Version:</span>
                <span class="text-sm font-medium text-gray-800 dark:text-white">1.0.0</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600 dark:text-gray-300">Last Updated:</span>
                <span class="text-sm font-medium text-gray-800 dark:text-white">February 26, 2026</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-gray-600 dark:text-gray-300">Framework:</span>
                <span class="text-sm font-medium text-gray-800 dark:text-white">DeepAgents</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HelpDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      activeTab: 'overview',
      faqOpen: {
        1: false,
        2: false,
        3: false,
        4: false
      }
    }
  },
  methods: {
    close() {
      this.$emit('update:visible', false)
    },
    toggleFaq(id) {
      this.faqOpen[id] = !this.faqOpen[id]
    }
  }
}
</script>

<style scoped>
/* Component-specific styles can be added here */
</style>