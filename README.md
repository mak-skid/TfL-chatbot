# TfL_chatbot

### Introduction
  Getting around London with the well-connected, yet vast, complex London public transport network can be quite challenging for non-locals. Although Google Maps provides users a comprehensive route navigation with effective visuals when getting around London, users might struggle to locate themselves on the map. The TfL-Chatbot provides simple yet more interactive navigation in a conversational form. Luckily, with the help of Transport for London’s Unified API, I was able to make the chatbot provide real-time travel information unlike other general-purpose chatbots such as ChatGPT, and can assist users to navigate themselves to their destination without worry. 

### How to run
In order to run the chatbot, run Main.py!

### Chatbot Architecture
#### Functionality
  TfL-Chatbot has mainly three functionalities: route searching, fare searching, and line information searching. Firstly, the chatbot takes in a user input and analyses the user’s intention. If the user is asking about his journey (such as fare, the line status of his route), it further processes the input and extracts his starting station or bus stop and destination from it. If the extracted information is not enough or is ambiguous, the chatbot asks the user back with a list of possible stations and stops to clarify where he is starting from and going to. With enough information gathered, it sends a request to TfL Unified API to retrieve suitable data and then processes the received data and responds to the user with the information. It also handles having small talk and answering general questions about the Transport for London public transport system such as payment methods.

#### Implementation
<img width="517" alt="Screenshot 2024-03-02 at 12 55 05" src="https://github.com/mak-skid/TfL-chatbot/assets/86308657/e6b4a7a5-999e-4b7a-be8b-fc2001471b1b">

<img width="448" alt="Screenshot 2024-03-02 at 12 55 27" src="https://github.com/mak-skid/TfL-chatbot/assets/86308657/acbb1de6-7a80-4e54-92af-b9bd45e74f54">

### Conversational Design
<img width="350" alt="Screenshot 2024-03-02 at 12 59 12" src="https://github.com/mak-skid/TfL-chatbot/assets/86308657/4698d0cc-f3de-4f31-8bac-4b894bb28006">

### Dataset used (modified and added)
https://github.com/anthonyckleung/Travel-Chatbot
https://github.com/microsoft/botframework-cli/blob/main/packages/qnamaker/docs/chit-chat-dataset.md
