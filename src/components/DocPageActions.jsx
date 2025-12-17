import React from 'react';
import PersonalizeButton from './PersonalizeButton';
import TranslateButton from './TranslateButton';
import styles from './DocPageActions.module.css';

/**
 * DocPageActions - Adds Personalize and Translate buttons to documentation pages
 *
 * Usage: Add to any markdown file:
 * import DocPageActions from '@site/src/components/DocPageActions';
 * <DocPageActions chapter="chapter-01" />
 */
export default function DocPageActions({ chapter }) {
  if (!chapter) {
    console.warn('DocPageActions: chapter prop is required');
    return null;
  }

  return (
    <div className={styles.docPageActions}>
      <div className={styles.actionsContainer}>
        <PersonalizeButton chapter={chapter} />
        <TranslateButton chapter={chapter} />
      </div>
    </div>
  );
}
