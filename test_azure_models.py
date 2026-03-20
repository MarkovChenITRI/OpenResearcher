"""
Test script to check available Azure OpenAI models and test o3 support
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_model(deployment_name):
    """Test if a model deployment works"""
    try:
        from utils.azure_openai_generator import AzureOpenAIAsyncGenerator
        
        print(f"\n{'='*60}")
        print(f"Testing deployment: {deployment_name}")
        print(f"{'='*60}")
        
        async with AzureOpenAIAsyncGenerator(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            deployment_name=deployment_name,
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            use_native_tools=False
        ) as generator:
            response = await generator.chat_completion(
                messages=[{"role": "user", "content": "Say 'Hello' if you can hear me."}],
                max_tokens=50,
                temperature=0.7
            )
            
            content = response['choices'][0]['message']['content']
            print(f"✅ SUCCESS: {deployment_name}")
            print(f"Response: {content}")
            return True
            
    except Exception as e:
        print(f"❌ FAILED: {deployment_name}")
        print(f"Error: {str(e)[:200]}")
        return False

async def main():
    """Test multiple model deployments"""
    print("\n" + "="*60)
    print("🔍 Azure OpenAI Model Availability Checker")
    print("="*60)
    
    # Current deployment
    current_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4")
    print(f"\n📌 Current deployment in .env: {current_deployment}")
    
    # Test current deployment
    await test_model(current_deployment)
    
    # Test o3 models (if they exist)
    print("\n" + "="*60)
    print("🧪 Testing o3 Series Models")
    print("="*60)
    
    o3_models = ["o3", "o3-mini", "o1", "o1-mini", "o1-preview"]
    
    for model in o3_models:
        await asyncio.sleep(1)  # Avoid rate limits
        await test_model(model)
    
    # Test GPT-4o models
    print("\n" + "="*60)
    print("🧪 Testing GPT-4o Series Models")
    print("="*60)
    
    gpt4o_models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    
    for model in gpt4o_models:
        await asyncio.sleep(1)
        await test_model(model)
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
    print("\nNOTE: Available models depend on your Azure OpenAI resource region.")
    print("Go to Azure Portal → Your OpenAI Service → Deployments")
    print("to see all available model deployments.")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
