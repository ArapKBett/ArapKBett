// lib/news.js
import axios from 'axios';

const API_KEY = 'YOUR_NEWSAPI_KEY';
const BASE_URL = 'https://newsapi.org/v2';

export const fetchNews = async (category = 'general') => {
  try {
    const response = await axios.get(`${BASE_URL}/top-headlines`, {
      params: {
        category,
        country: 'us',
        apiKey: API_KEY,
      },
    });
    return response.data.articles;
  } catch (error) {
    console.error('Error fetching news:', error);
    return [];
  }
};
