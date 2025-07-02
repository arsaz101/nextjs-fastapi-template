# Documentation Updater

This is a sample documentation file to test the AI-powered documentation updater.

## Introduction

This tool helps you keep your documentation up to date using AI suggestions.

## Features

- AI-powered suggestions for documentation updates
- Automatic file backup before making changes
- Review and approve/reject/edit suggestions
- Support for Markdown files

## Usage

1. Enter your documentation update query
2. Review AI-generated suggestions
3. Approve, reject, or edit suggestions
4. Apply changes to your files

## API Reference

### Authentication

The API uses JWT tokens for authentication.

### Endpoints

- `POST /doc-updates/suggest` - Get AI suggestions
- `POST /doc-updates/apply` - Apply approved changes
- `GET /doc-updates/files` - List documentation files
- `GET /doc-updates/backups` - List backup files

## Configuration

Set up your environment variables:

```env
OPENAI_API_KEY=your-api-key-here
DATABASE_URL=your-database-url
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
