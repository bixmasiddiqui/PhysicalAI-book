/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Foundations of Physical AI',
      items: [
        'chapter-01',
        'chapter-02',
        'chapter-03',
      ],
    },
    {
      type: 'category',
      label: 'Robotics Hardware & AI',
      items: [
        'chapter-04',
        'chapter-05',
        'chapter-06',
      ],
    },
    {
      type: 'category',
      label: 'Motion, Control & Applications',
      items: [
        'chapter-07',
        'chapter-08',
        'chapter-09',
        'chapter-10',
      ],
    },
  ],
};

module.exports = sidebars;
