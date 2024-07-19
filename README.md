
# Pinecone Assistants Sample App

Use this sample app to interact with assistants you have created in the Pinecone console. This app allows you to create a deployable Next.js application to interact with your assistants and their uploaded files.

### Built With

- Pinecone Assistant
- Next.js + Python + Tailwind + Flask Backend
- Node version 20 or higher

---
## Running the Sample App

### Want to move fast?

Use `npx create-pinecone-app` to adopt this project quickly.
This will clone the project, and prompt you for necessary secrets. Make sure you've created your assistant and uploaded your files in the Pinecone console at this point.

### Create a Pinecone API key
**Grab an API key [here](https://app.pinecone.io)**

Before you start, this application requires you to build Pinecone Assistant in the Console first. You'll also need to upload files to this assistant. Any set of PDF files will do!

### Start the project

In order to isolate Python dependencies, create a conda environment and install the dependencies there.

```bash
conda create -n pinecone-assistant-env python=3.12
conda activate pinecone-assistant-env
```

#### Dependency Installation

```bash
cd pinecone-assistant && npm install --force
```

Then, launch the app:

```bash
npm run dev
```
This will start the backend Python server as well as install dependencies in your conda environment. Navigate to localhost:3000 to see the app.


## Project structure

TODO

---
## Troubleshooting
Experiencing any issues with the sample app?
Submit an issue, create a PR, or post in our community forum!
---