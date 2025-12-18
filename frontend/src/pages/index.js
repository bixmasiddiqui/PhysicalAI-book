import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Learning 
          </Link>
        </div>
      </div>
    </header>
  );
}

function FeatureItem({title, description, icon}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center" style={{fontSize: '3rem', marginBottom: '1rem'}}>
        {icon}
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

function HomepageFeatures() {
  const features = [
    {
      title: 'AI-Powered Learning',
      icon: '🤖',
      description: 'Interactive AI chatbot to answer your questions and personalize content to your learning style.',
    },
    {
      title: 'Comprehensive Coverage',
      icon: '📚',
      description: 'From fundamentals to advanced topics in Physical AI and Humanoid Robotics - all in one place.',
    },
    {
      title: 'Practical & Industry-Ready',
      icon: '⚡',
      description: 'Real-world examples, code implementations, and skills needed for careers in robotics.',
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {features.map((props, idx) => (
            <FeatureItem key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

function CourseOverview() {
  return (
    <section className={styles.courseOverview}>
      <div className="container">
        <h2 className="text--center" style={{marginBottom: '2rem'}}>What You'll Learn</h2>
        <div className="row">
          <div className="col col--6">
            <h3>📖 Core Topics</h3>
            <ul>
              <li>Fundamentals of Physical AI Systems</li>
              <li>Sensors, Actuators & Control Systems</li>
              <li>Machine Learning for Robotics</li>
              <li>Motion Planning & Navigation</li>
              <li>Computer Vision & Perception</li>
              <li>Real-world Applications & Ethics</li>
            </ul>
          </div>
          <div className="col col--6">
            <h3>💼 Career Preparation</h3>
            <ul>
              <li>Programming in Python, C++, and ROS</li>
              <li>Hands-on projects and exercises</li>
              <li>Industry best practices</li>
              <li>Job roles and career paths</li>
              <li>Interview preparation tips</li>
              <li>Portfolio-worthy projects</li>
            </ul>
          </div>
        </div>
        <div className="text--center" style={{marginTop: '2rem'}}>
          <Link
            className="button button--primary button--lg"
            to="/docs/intro">
            Browse All Chapters
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Master Physical AI and Humanoid Robotics with this comprehensive, AI-powered interactive textbook">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <CourseOverview />
      </main>
    </Layout>
  );
}
