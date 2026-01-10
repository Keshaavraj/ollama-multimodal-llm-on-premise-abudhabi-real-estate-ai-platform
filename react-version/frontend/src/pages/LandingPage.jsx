import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaRobot, FaImage, FaMicrophone, FaBolt, FaChartLine, FaServer } from 'react-icons/fa';
import './LandingPage.css';

function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <FaRobot size={40} />,
      title: 'AI-Powered Assistant',
      description: 'Llama 3.1 8B & LLaVA 7B models for intelligent conversations'
    },
    {
      icon: <FaImage size={40} />,
      title: 'Image Analysis',
      description: 'Upload property images for instant AI-powered analysis'
    },
    {
      icon: <FaMicrophone size={40} />,
      title: 'Voice Integration',
      description: 'Speech-to-text and text-to-speech for hands-free interaction'
    },
    {
      icon: <FaBolt size={40} />,
      title: 'Real-time Processing',
      description: 'Low-latency responses with performance metrics tracking'
    },
    {
      icon: <FaChartLine size={40} />,
      title: 'Analytics Dashboard',
      description: 'Monitor tokens, latency, and model performance in real-time'
    },
    {
      icon: <FaServer size={40} />,
      title: 'On-Premise Models',
      description: 'Fully local Ollama deployment with FastAPI backend'
    }
  ];

  const techStack = [
    { name: 'Llama 3.1 8B', type: 'Text Model' },
    { name: 'LLaVA 7B', type: 'Vision Model' },
    { name: 'FastAPI', type: 'Backend' },
    { name: 'React + Vite', type: 'Frontend' },
    { name: 'Ollama', type: 'LLM Runtime' }
  ];

  return (
    <div className="landing-page">
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge-dot"></span>
            Powered by Local LLMs
          </div>
          <h1 className="hero-title">
            Abu Dhabi Real Estate
            <span className="gradient-text"> AI Assistant</span>
          </h1>
          <p className="hero-subtitle">
            Experience next-generation property search with on-premise AI models,
            real-time analytics, and multi-modal interactions
          </p>

          <div className="hero-actions">
            <button className="btn-primary" onClick={() => navigate('/chat')}>
              Launch Assistant
              <span className="btn-arrow">→</span>
            </button>
            <button className="btn-secondary" onClick={() => {
              document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
            }}>
              View Features
            </button>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-value">2</div>
              <div className="stat-label">AI Models</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">&lt;2s</div>
              <div className="stat-label">Avg Response</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">100%</div>
              <div className="stat-label">Local Processing</div>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="floating-card card-1">
            <div className="card-icon">🏠</div>
            <div className="card-text">Property Analysis</div>
          </div>
          <div className="floating-card card-2">
            <div className="card-icon">🤖</div>
            <div className="card-text">AI Response</div>
          </div>
          <div className="floating-card card-3">
            <div className="card-icon">📊</div>
            <div className="card-text">Real-time Metrics</div>
          </div>
        </div>
      </div>

      <section id="features" className="features-section">
        <div className="section-header">
          <h2>Powerful Features</h2>
          <p>Everything you need for intelligent real estate assistance</p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="tech-section">
        <div className="section-header">
          <h2>Technology Stack</h2>
          <p>Built with cutting-edge AI and modern web technologies</p>
        </div>

        <div className="tech-grid">
          {techStack.map((tech, index) => (
            <div key={index} className="tech-card">
              <div className="tech-name">{tech.name}</div>
              <div className="tech-type">{tech.type}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Experience AI-Powered Real Estate?</h2>
          <p>Start exploring properties with intelligent assistance</p>
          <button className="btn-primary-large" onClick={() => navigate('/chat')}>
            Get Started Now
          </button>
        </div>
      </section>

      <footer className="landing-footer">
        <p>Built with React, Vite, FastAPI, and Ollama • On-Premise LLM Deployment</p>
      </footer>
    </div>
  );
}

export default LandingPage;
