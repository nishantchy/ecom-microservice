import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import { connectDB } from "./config/database";
import { startOrderConsumer } from "./consumer/order.consumer";

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Home route - API documentation
app.get("/", (_req, res) => {
  res.send(`
      <h1>Email Service API</h1>
    `);
});

// Start server function
const startServer = async () => {
  try {
    await connectDB();

    await startOrderConsumer();

    // Start the server
    const PORT = process.env.PORT || 5000;
    app.listen(PORT, () => {
      console.log(`Server is running on http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
};

// Start the application
startServer();
