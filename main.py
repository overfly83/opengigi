from agent import AutonomousAgent
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保设置了OpenAI API密钥
if not os.getenv("OPENAI_API_KEY"):
    print("请在.env文件中设置OPENAI_API_KEY")
    exit(1)

def main():
    """主函数"""
    print("=== 初始化自主决策Agent ===")
    
    # 创建Agent实例
    agent = AutonomousAgent()
    
    print("Agent初始化成功！")
    print("\n请输入您的目标：")
    
    # 示例目标
    # goal = "创建一个简单的待办事项应用，包含添加、删除和标记完成功能"
    # goal = "为周末制定一个详细的旅行计划，包括景点、交通和住宿"
    # goal = "写一篇关于人工智能发展趋势的文章"
    
    # 从用户输入获取目标
    goal = input("目标: ")
    
    if not goal:
        print("目标不能为空")
        return
    
    print(f"\n=== 开始处理目标 ===")
    print(f"目标: {goal}")
    
    # 运行完整的决策闭环
    result = agent.run(goal)
    
    print(f"\n=== 处理完成 ===")
    print(f"迭代次数: {result['iterations'] + 1}")
    print(f"目标完成状态: {'完成' if result['completed'] else '未完成'}")
    
    # 保存结果到文件
    import json
    with open("agent_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 agent_result.json 文件")

if __name__ == "__main__":
    main()