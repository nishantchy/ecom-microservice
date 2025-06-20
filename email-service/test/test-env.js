require("dotenv").config();

console.log("=== Environment Variables Test ===");
console.log("EMAIL_USER:", process.env.EMAIL_USER);
console.log("EMAIL_PASS:", process.env.EMAIL_PASS ? "***HIDDEN***" : "NOT SET");
console.log("MONGO_URI:", process.env.MONGO_URI);
console.log("PORT:", process.env.PORT);

if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
  console.log("Email credentials are loaded correctly");
} else {
  console.log("Email credentials are missing");
}

console.log("=== Current working directory ===");
console.log(process.cwd());

console.log("=== .env file check ===");
const fs = require("fs");
const path = require("path");
const envPath = path.join(process.cwd(), ".env");
if (fs.existsSync(envPath)) {
  console.log(".env file exists at:", envPath);
} else {
  console.log(".env file not found at:", envPath);
}
