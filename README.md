
Pinecone Assistants Sample App

!image
Use this sample app to interact with assistants you have created in the Pinecone console. This app allows you to create a deployable Next.js application to interact with your assistants and their uploaded files.
!image

This app demonstrates how to programmatically bootstrap a custom knowledge base based on a Pinecone vector database with files uploaded to your assistants.
Built With
Pinecone Serverless
Next.js + Tailwind
Node version 20 or higher
---
Running the Sample App
Want to move fast?
Use npx create-pinecone-app to adopt this project quickly.
Create a Pinecone API key
Grab an API key here
<div id="pinecone-connect-widget"></div>
This application will detect if you already have an index of the same name as the value
you set in your PINECONE_INDEX environment variable.
If you don't already have an index, the application will create one for you with the correct dimensions.
Create an Assistant in Pinecone
Create a new assistant in the Pinecone console and upload your files.
Start the project
Requires Node version 20+
Dependency installation
From the project root directory, run the following command.
force
Make sure you have populated the client .env with relevant keys.
"
Start the app.
dev
Project structure
In this example, we opted to use a standard Next.js application structure.
Frontend Client
The frontend uses Next.js, Tailwind, and custom React components to power the search experience. It also leverages API routes to make calls to the server to initiate bootstrapping of the Pinecone vector database as a knowledge store, and to fetch relevant document chunks for the UI.
Backend Server
This project uses Next.js API routes to handle file chunking, upsertion, and context provision, etc. Learn more about the implementation details below.
Simple semantic search
This project uses a basic semantic search architecture that achieves low latency natural language search across all embedded documents. When the app is loaded, it performs background checks to determine if the Pinecone vector database needs to be created and populated.
Componentized suggested search interface
To make it easier for you to clone this app as a starting point and quickly adopt it to your own purposes, we've built the search interface as a component that accepts a list of suggested searches and renders them as a dropdown, helping the user find things:
You can define your suggested searches in your parent component:
>
This means you can pass in any suggested searches you wish given your specific use case.
The SearchForm component is exported from src/components/SearchForm.tsx. It handles:
Displaying suggested searches
Allowing the user to search, or clear the input
Providing visual feedback to the user that the search is in progress
Local document processing via a bootstrapping service
We store several example files in the codebase, so that developers cloning and running the app locally can immediately build off the same experience being demonstrated by the Pinecone Assistants app running on our Docs site.
We use Langchain to parse the files, convert them into chunks, and embed them. We store the resulting vectors in the Pinecone vector database.
Knowledge base bootstrapping
This project demonstrates how to programmatically bootstrap a knowledge base backed by a Pinecone vector database using files uploaded to your assistants.
}


When a user accesses the app, it runs a check to determine if the bootstrapping procedure needs to be run.
If the Pinecone index does not already exist, or if it exists but does not yet contain vectors, the bootstrapping procedure is run.
The bootstrapping procedure:
Creates the Pinecone index specified by the PINECONE_INDEX environment variable
Loads metadata from the docs/db.json file
Loads all documents in the docs directory
Merges extracted metadata with documents based on filename
Splits text into chunks
Assigns unique IDs to each split and flattens metadata
Upserts each chunk to the Pinecone vector database, in batches
---
Troubleshooting
Experiencing any issues with the sample app?
Submit an issue, create a PR, or post in our community forum!
---