import express from "express";
import { sendOrderConfirmation } from "../controller/email.controller";

const router = express.Router();

router.post("/send", sendOrderConfirmation);

export default router;
