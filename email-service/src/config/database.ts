import mongoose from "mongoose";

let isConnected = false;

export const connectDB = async () => {
  if (isConnected) {
    console.log("MongoDB already connected");
    return;
  }

  try {
    const mongoUri =
      process.env.MONGO_URI || "mongodb://localhost:27017/email-service";

    await mongoose.connect(mongoUri);

    isConnected = true;
    console.log(
      `MongoDB Connected: ${mongoose.connection.host}, ${mongoose.connection.name}`
    );

    // Handle connection events
    mongoose.connection.on("error", (err) => {
      console.error("MongoDB connection error:", err);
      isConnected = false;
    });

    mongoose.connection.on("disconnected", () => {
      console.log("MongoDB disconnected");
      isConnected = false;
    });
  } catch (error) {
    console.error("MongoDB connection error:", error);
    process.exit(1);
  }
};
