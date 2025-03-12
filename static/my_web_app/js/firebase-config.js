// firebase-config.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCwA7ry3hn_8ghm1j9ichHeW010DYRnaXs",
  authDomain: "ai01-51d16.firebaseapp.com",
  projectId: "ai01-51d16",
  storageBucket: "ai01-51d16.appspot.com",
  messagingSenderId: "676297729756",
  appId: "1:676297729756:web:e39792eaaf65b1b7ebb619",
  measurementId: "G-E33XQCBVW9"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const provider = new GoogleAuthProvider();
