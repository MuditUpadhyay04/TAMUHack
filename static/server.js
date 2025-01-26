const OpenAI = require("openai");
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
app.use(bodyParser.json());
app.use(cors());

const openai = new OpenAI({
  apiKey: "key",
});

app.post("/chat", async (req, res) => {
  const { message } = req.body;

  if (!message) {
    return res.status(400).json({ error: "Message content is required" });
  }

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo', // Replace with "gpt-4" or the appropriate model
      messages: [{ role: 'user', content: message }],
    });

    res.json({ response: completion.choices[0].message.content });
  } catch (error) {
    console.error("Error:", error.message);
    res.status(500).json({ error: "Failed to communicate with ChatGPT" });
  }
});

app.listen(5005, () => {
  console.log("Server is running on http://localhost:5005");
});