Thai: the assistant who care!
Description
Thai is an intelligent llm chatbot designed to provide users with information about various government schemes, nutritional advice, and guidance related to pregnancy and child care. Utilizing advanced AI models, this chatbot can understand user queries and retrieve relevant information from a preloaded dataset. The project leverages state-of-the-art natural language processing techniques to ensure accurate and helpful responses.

Who is This For?
This project is aimed at:

Expectant Mothers: Providing essential information regarding pregnancy, health tips, and available government schemes.
Parents: Assisting in finding reliable information about child care and nutrition.
Healthcare Providers: Offering a tool to educate patients about various health schemes and nutritional guidelines.
Developers and Researchers: Anyone interested in developing conversational AI applications or exploring the integration of machine learning models for real-world applications.
Features
Natural Language Processing: Understands and processes user queries in natural language.
Retrieval QA System: Uses advanced retrieval techniques to fetch accurate information based on user questions.
Multiple Data Sources: Supports various formats for information retrieval, including PDFs and other document types.
Interactive User Interface: Built with Chainlit for a user-friendly chat experience.
Custom Prompting: Tailored prompts to ensure the chatbot provides concise and relevant answers.
Installation
To set up the project locally, follow these steps:

Clone the repository:

bash
Copy code
git clone https://github.com/Madhavan-no1/Thai.git
cd thai
Create a virtual environment (optional but recommended):


bash

pip install -r requirements.txt
Usage
Ensure you have the necessary files and embeddings loaded in the specified DB_FAISS_PATH.
Start the chatbot server:

chainlit run chat.py
Open your web browser and navigate to http://localhost:8501 to interact with the bot.
## API Reference

#### Get all items

```http
  GET /api/items
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `HF_TOKEN` | `string` | **Required**. Your API key |

#### Get item

```http
  GET /api/items/${id}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `VISION API`      | `string` | **Required**. Id of item to fetch |



## Authors

- [@Madhavan M](https://www.github.com/Madhavan-no1)

- [@Dhaanush N V](https://www.github.com/dhaanush)
- [@Dhinesh Kumar A](https://www.github.com/Dhineshsaff)
- [@Hemachandran](https://www.github.com/hemazhandranzz)
## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Tech Stack

Thai CHAT - Microsoft's Phi 3.7b parameters, Streamlit,
Thai Nutrient Analyser - Vision AI,flask,python scripts to run local model voice assistant
Thai Pill reminder - uses google calendar to remind the user and a simple flask application for frontend.


