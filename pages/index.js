// pages/index.js
import { useState, useEffect } from 'react';
import { fetchNews } from '../lib/news';

export default function Home() {
  const [articles, setArticles] = useState([]);
  const [category, setCategory] = useState('general');

  useEffect(() => {
    const getNews = async () => {
      const news = await fetchNews(category);
      setArticles(news);
    };
    getNews();
  }, [category]);

  return (
    <div>
      <h1>News Aggregator</h1>
      <select onChange={(e) => setCategory(e.target.value)} value={category}>
        <option value="general">General</option>
        <option value="business">Business</option>
        <option value="entertainment">Entertainment</option>
        <option value="health">Health</option>
        <option value="science">Science</option>
        <option value="sports">Sports</option>
        <option value="technology">Technology</option>
      </select>
      <div>
        {articles.map((article, index) => (
          <div key={index}>
            <h2>{article.title}</h2>
            <p>{article.description}</p>
            <a href={article.url} target="_blank" rel="noopener noreferrer">Read more</a>
          </div>
        ))}
      </div>
    </div>
  );
}
