import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import cookieParser from 'cookie-parser';
import morgan from 'morgan';
import helmet from 'helmet';

dotenv.config();

const app = express();

// Apply CORS middleware
app.use(cors({
    credentials: true,
    origin: process.env.FRONTEND_URL
}));

app.use(express.json());
app.use(cookieParser());
app.use(morgan('dev')); // You can specify the logging format ('dev' is common)
app.use(helmet({
    // This allows the app not to show errors in case of cross-origin issues
    crossOriginResourcePolicy: false
}));
const PORT = process.env.PORT || 8080;
// show message in the browser
app.get("/", (request,response)=>{
    response.json({
        message : "Server is running"
    })
})

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
