# OpenAI Integration Setup

This project includes AI-powered documentation suggestions using OpenAI's API.

## Setup Instructions

### 1. Install OpenAI Package

```bash
pip install openai
```

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key

### 3. Configure Environment

Add your OpenAI API key to your `.env` file:

```env
# OpenAI API Key (optional - for AI-powered doc suggestions)
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Usage

The AI service will automatically:

- Use OpenAI API when the key is provided
- Fall back to basic suggestions when no key is available
- Handle errors gracefully

### 5. Cost Considerations

- Uses GPT-4o-mini for cost efficiency
- Limited to 1000 tokens per request
- Monitor usage in your OpenAI dashboard

## Features

- **Smart Suggestions**: AI analyzes user queries and provides specific documentation update suggestions
- **Fallback Mode**: Works without API key using basic suggestions
- **Error Handling**: Graceful degradation when API is unavailable
- **Cost Optimized**: Uses efficient model and token limits

## Testing

1. Start the FastAPI backend: `uvicorn app.main:app --reload`
2. Start the Next.js frontend: `pnpm dev`
3. Visit `/doc-update` and enter a query
4. The AI will generate suggestions based on your input
