import { Request, Response, NextFunction } from "express";

// Define a consistent user type
export interface IRequestUser {
  id: string;
  role?: string;
  isSuperAdmin?: boolean;
  [key: string]: any;
}

// Define a consistent AuthRequest type that extends Express Request
export interface AuthRequest extends Request {
  user: IRequestUser;
}

// Define a generic type for async request handlers
export type AsyncRequestHandler = (
  req: Request,
  res: Response,
  next?: NextFunction
) => Promise<any>;

export type SyncRequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction
) => void;
