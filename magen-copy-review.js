const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  Header, Footer, PageNumber, LevelFormat
} = require('/usr/local/lib/node_modules_global/lib/node_modules/docx');
const fs = require('fs');

const TEAL   = '00AEAC';
const DARK   = '1A1A2E';
const RED    = 'CC0000';
const ORANGE = 'C05000';
const GRAY   = '555555';
const LGRAY  = 'F5F5F5';
const WHITE  = 'FFFFFF';

// A small label like "HEADLINE" above a copy block
function label(text) {
  return new Paragraph({
    children: [new TextRun({ text: text.toUpperCase(), font: 'Arial', size: 16, bold: true, color: TEAL })],
    spacing: { before: 280, after: 60 },
  });
}

// The actual copy — large and easy to read
function copy(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({
      text,
      font: 'Arial',
      size: opts.large ? 28 : 24,
      color: opts.color || DARK,
      italics: opts.italics || false,
      bold: opts.bold || false,
    })],
    spacing: { before: 0, after: 80 },
    shading: opts.shade ? { fill: LGRAY, type: ShadingType.CLEAR } : undefined,
  });
}

// Placeholder — red, clearly marked
function ph(text) {
  return new Paragraph({
    children: [new TextRun({ text: '[PLACEHOLDER] ' + text, font: 'Arial', size: 22, color: RED, italics: true })],
    spacing: { before: 0, after: 80 },
    shading: { fill: 'FFF0F0', type: ShadingType.CLEAR },
  });
}

// Decision needed — orange
function decision(text) {
  return new Paragraph({
    children: [new TextRun({ text: '[DECISION NEEDED] ' + text, font: 'Arial', size: 20, color: ORANGE, bold: true })],
    spacing: { before: 40, after: 80 },
    shading: { fill: 'FFF8F0', type: ShadingType.CLEAR },
  });
}

// Section divider
function divider() {
  return new Paragraph({
    children: [new TextRun({ text: '', size: 4 })],
    border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: 'DDDDDD', space: 4 } },
    spacing: { before: 360, after: 360 },
  });
}

// Section header
function section(num, title) {
  return new Paragraph({
    pageBreakBefore: num > 1,
    children: [
      new TextRun({ text: `${num}  `, font: 'Arial', size: 40, bold: true, color: TEAL }),
      new TextRun({ text: title.toUpperCase(), font: 'Arial', size: 40, bold: true, color: DARK }),
    ],
    spacing: { before: 0, after: 40 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: TEAL, space: 6 } },
  });
}

function space() {
  return new Paragraph({ children: [new TextRun('')], spacing: { before: 40, after: 40 } });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 24 } } },
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, right: 1440, bottom: 1080, left: 1440 } }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [
            new TextRun({ text: 'Magen Website  —  Copy Review', font: 'Arial', size: 18, color: TEAL, bold: true }),
            new TextRun({ text: '   |   April 2026', font: 'Arial', size: 18, color: GRAY }),
          ],
          border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: 'DDDDDD', space: 4 } },
          spacing: { after: 80 },
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ text: 'Page ', font: 'Arial', size: 16, color: 'AAAAAA' }),
            new TextRun({ children: [PageNumber.CURRENT], font: 'Arial', size: 16, color: 'AAAAAA' }),
          ],
          border: { top: { style: BorderStyle.SINGLE, size: 2, color: 'EEEEEE', space: 4 } },
          spacing: { before: 80 },
        })]
      })
    },
    children: [

      // COVER
      new Paragraph({
        children: [new TextRun({ text: 'Magen for Jewish Communities', font: 'Arial', size: 64, bold: true, color: DARK })],
        spacing: { before: 720, after: 80 },
      }),
      new Paragraph({
        children: [new TextRun({ text: 'Website Copy Review', font: 'Arial', size: 36, color: TEAL })],
        spacing: { before: 0, after: 80 },
      }),
      new Paragraph({
        children: [new TextRun({ text: 'April 2026  ·  Draft 1', font: 'Arial', size: 22, color: GRAY })],
        spacing: { before: 0, after: 480 },
      }),
      new Paragraph({
        children: [new TextRun({
          text: 'This document contains only the copy from the Magen homepage, organized section by section for review and editing. Use Google Docs comments to mark feedback on any line.',
          font: 'Arial', size: 22, color: GRAY,
        })],
        spacing: { before: 0, after: 160 },
      }),
      new Paragraph({
        children: [
          new TextRun({ text: 'Red items ', font: 'Arial', size: 20, bold: true, color: RED }),
          new TextRun({ text: 'are placeholders that need content from Magen.  ', font: 'Arial', size: 20, color: GRAY }),
          new TextRun({ text: 'Orange items ', font: 'Arial', size: 20, bold: true, color: ORANGE }),
          new TextRun({ text: 'need a decision.', font: 'Arial', size: 20, color: GRAY }),
        ],
        spacing: { before: 0, after: 720 },
      }),

      // ── 1. CRISIS BAR ──
      section(1, 'Crisis Bar'),
      space(),
      new Paragraph({
        children: [new TextRun({ text: 'Persistent bar above the navigation on all pages.', font: 'Arial', size: 18, color: GRAY, italics: true })],
        spacing: { before: 0, after: 160 },
      }),
      label('Full bar text'),
      copy('If you or someone is in immediate danger, call emergency services now:   Israel: 100  ·  US: 911  ·  UK: 999', { shade: true }),
      label('Magen hotline'),
      decision('Star number for Magen hotline — CEO to provide'),
      label('Hours'),
      copy('Available 24/6'),

      // ── 2. NAV ──
      section(2, 'Navigation'),
      space(),
      label('Primary nav items'),
      copy('Safety & Healing', { shade: true }),
      copy('Advocacy & Investigations', { shade: true }),
      copy('Community & Network', { shade: true }),
      copy('Resources', { shade: true }),
      copy('Magen', { shade: true }),
      copy('Donate →  (button)', { shade: true }),

      // ── 3. HERO ──
      section(3, 'Hero'),
      space(),
      label('Headline'),
      copy('The first step in your journey to healing is safety.\nSafety begins with being heard.', { large: true }),
      decision('Hero headline — confirm with CEO'),
      space(),
      label('Subheadline'),
      copy('Whether you\'re a survivor, family member, or concerned friend — we\'re here to listen.'),
      space(),
      label('CTA button'),
      copy('Get in touch'),
      space(),
      label('Reassurance line'),
      copy('Confidential  ·  Professional  ·  Available 24/6'),

      // ── 4. SAFETY & HEALING ──
      section(4, 'Safety & Healing — How Magen Helps'),
      space(),
      label('Eyebrow'),
      copy('Safety & Healing with Magen'),
      space(),
      label('Headline'),
      copy('How Magen helps', { large: true }),
      space(),
      label('Intro'),
      copy('There are two things Magen is here to do. They go in order — and we\'re with you through both.'),
      space(),
      label('Stage 01 — headline'),
      copy('Making sure you\'re safe'),
      space(),
      label('Stage 01 — body'),
      copy('The first thing — before anything else — is safety. That means physical safety, but it also means emotional and psychological safety.'),
      copy('Sometimes you\'re in immediate danger. Sometimes you\'re not sure where you stand. Either way, getting safe is a process, and that process is where everything begins.'),
      space(),
      label('Stage 02 — headline'),
      copy('Working through your experience'),
      space(),
      label('Stage 02 — body'),
      copy('Once you\'re safe — or in the process of getting there — you have the opportunity to work through what happened to you. To process it, understand it, and move through it.'),
      copy('A dedicated case manager at Magen stays with you through this — coordinating therapy, support, and anything else you need, so you\'re not managing it alone.'),
      copy('You\'re not trapped by your experience. With the right support, this becomes part of your story — not the whole of it.'),

      // ── 5. PROGRAMS ──
      section(5, 'Programs'),
      space(),
      label('Eyebrow'),
      copy('Magen\'s Programs'),
      space(),
      label('Headline'),
      copy('What kind of help do you need?', { large: true }),

      divider(),
      label('Program — 24/6 Crisis Hotline'),
      copy('Someone to talk to right now'),
      copy('If something feels wrong or unsafe, call Magen\'s crisis hotline to speak with someone caring and experienced. You\'ll learn your options and get immediate support.'),
      label('CTA'),
      copy('Call now →'),

      divider(),
      label('Program — Therapy Referrals'),
      copy('Find the right therapist for you'),
      copy('Get connected to experienced, trauma-informed therapists offering evidence-based care — matched to your needs, background, and where you are in your journey.'),
      label('CTA'),
      copy('Find therapy →'),

      divider(),
      label('Program — Peer Support'),
      copy('You\'re not the only one'),
      copy('Join a facilitated peer group tailored to shared experiences — a space for connection, understanding, and the quiet power of being with people who truly get it.'),
      label('CTA'),
      copy('Join a group →'),

      divider(),
      label('Program — Government Assistance (Coming Soon)'),
      copy('Navigate your benefits'),
      copy('Understand your rights and get guided support navigating Bituach Leumi benefits — which are often difficult to access without someone who knows the system.'),
      label('CTA'),
      copy('Find out more →'),

      // ── 6. VOICES ──
      section(6, 'People Love Magen'),
      space(),
      label('Eyebrow'),
      copy('People Love Magen'),
      space(),
      label('Headline'),
      copy('People Love Magen', { large: true }),
      space(),
      label('Intro'),
      copy('From survivors to social workers, from law enforcement to parents — Magen has earned deep trust from the people it serves and the professionals who work alongside it.'),

      divider(),
      label('Quote 1 — Survivor'),
      copy('"Magen has literally saved many lives. Including my own. Shana was like my own personal cheerleading squad. Continue your avodas hakodesh, Shana and the Magen team. Continue saving lives."', { italics: true }),
      label('Attribution'),
      copy('Anonymous Survivor  ·  Donation message'),

      divider(),
      label('Quote 2 — Revacha'),
      ph('Quote from senior Revacha official — to be provided by Magen'),
      label('Attribution'),
      ph('[Name]  ·  Senior Official, Revacha'),

      divider(),
      label('Quote 3 — Parents of a survivor'),
      ph('Quote from parents of a survivor — to be provided by Magen'),
      label('Attribution'),
      ph('[Name]  ·  Parents of a survivor'),

      // ── 7. BOOK CTA ──
      section(7, 'Book — Helise\'s Therapy Book'),
      space(),
      label('Eyebrow'),
      copy('New from Magen'),
      space(),
      label('Book title'),
      ph('Helise\'s book title — to be provided'),
      space(),
      label('Description'),
      ph('1–2 sentences: what the book is, who it\'s for, what it gives the reader — to be provided by Magen'),
      space(),
      label('CTA button'),
      copy('Get the book →'),
      space(),
      label('Book cover image'),
      ph('Book cover image file — to be provided by Magen'),

      // ── 8. TEAM ──
      section(8, 'Team'),
      space(),
      label('Eyebrow'),
      copy('The People Behind the Work'),
      space(),
      label('Headline'),
      copy('You Won\'t Do This Alone', { large: true }),
      space(),
      label('Intro'),
      copy('Magen\'s team of experienced professionals walks with you through every step — with care, expertise, and total commitment.'),
      space(),
      label('Team members shown'),
      decision('Confirm which team members to feature — should reflect relevant division'),
      copy('Shana Aaronson  ·  Executive Director', { shade: true }),
      copy('Sharon Weiss-Greenberg  ·  Chairwoman of the Board', { shade: true }),
      copy('Rabbi Yosef Blau  ·  Rabbinic Advisor', { shade: true }),
      copy('Ester Horovits  ·  Clinical Director  [photo needed]', { shade: true }),
      copy('Rikki Weiss  ·  Investigation Director  [photo needed]', { shade: true }),
      label('Link'),
      copy('Meet the full team →'),

      // ── 9. FAQ ──
      section(9, 'FAQ'),
      space(),
      new Paragraph({
        children: [new TextRun({ text: 'Questions and answers appear as an accordion on the page. Tagged with Schema.org markup for AI/search engine discoverability.', font: 'Arial', size: 18, color: GRAY, italics: true })],
        spacing: { before: 0, after: 200 },
      }),

      ...[
        ['What happens when I contact Magen for the first time?',
         'You don\'t need to prepare anything or be sure about what you want. When you reach out, you\'ll speak with a trained team member who will listen and understand your situation. There is no pressure to take immediate action — you can take things one step at a time. We will explain your options clearly so you can make informed decisions about what happens next.'],
        ['Is Magen\'s crisis hotline confidential?',
         'We treat every conversation with a high level of confidentiality and sensitivity. In most cases, your information is not shared without your permission. However, there are specific situations under Israeli law — particularly when there is an ongoing risk of harm or involvement of a minor — where there may be a legal obligation to report. If that becomes relevant, we will explain it to you clearly and support you through what it means, so you are not caught off guard.'],
        ['Will you report to the police if I contact you?',
         'Reaching out to Magen does not automatically mean a report will be made. In many cases, people can speak with us confidentially without any report being filed. However, under Israeli law, there are certain situations — especially involving minors or ongoing risk — where reporting may be required. If this applies, we will be transparent with you, explain the process, and support you through every step. Whenever possible, we aim to ensure you understand your options and are not facing decisions alone.'],
        ['What if I\'m not sure if what happened to me was abuse?',
         'You don\'t need to be certain before reaching out. Many people contact us because something didn\'t feel right, even if they don\'t have the words for it. We will listen without judgment, help you make sense of your experience, and support you in deciding what — if anything — you want to do next.'],
        ['What if I\'m scared to tell anyone or worried about how this could affect my family or community?',
         'That fear is very real, and you\'re not alone in feeling it. Many people worry about how speaking up might affect their family, reputation, or place in the community. You can talk to us to better understand your situation and your options before making any decisions. We approach every case with sensitivity to both your personal needs and your broader context.'],
        ['Do I need to be religious to use Magen\'s services?',
         'No. While we specialize in supporting people from Orthodox and traditional Jewish communities, our services are available to anyone who needs support. We bring an understanding of the cultural and religious dynamics many people navigate, but there is no requirement for religious observance.'],
        ['Are Magen\'s services free?',
         'Yes. Core services — including the crisis hotline, case management, and support groups — are provided free of charge. If you are connected with a therapist, costs may vary depending on the provider, insurance, or Bituach Leumi eligibility. We can help you understand your options.'],
        ['How does Magen\'s case management work?',
         'You are supported by one dedicated, experienced person who stays with you over time. They help coordinate everything you may need — including therapy referrals, legal guidance, navigating police processes, and accessing benefits such as Bituach Leumi. This means you don\'t have to manage everything alone or repeat your story to multiple people.'],
        ['Can you help me navigate legal processes or Bituach Leumi in Israel?',
         'Yes. We regularly support people in understanding and navigating Israeli systems — including police processes, legal options, and Bituach Leumi rights. We can explain what to expect, help you prepare, and connect you with trusted professionals, so you\'re not facing these systems alone.'],
        ['What kind of support is available for survivors of sexual abuse in Israel?',
         'Support can include confidential crisis support, ongoing case management, therapy referrals, legal advocacy, and peer support groups. Magen helps you access and coordinate these resources in a way that fits your situation — supporting both your emotional needs and practical next steps.'],
      ].flatMap(([q, a]) => [
        divider(),
        label('Question'),
        copy(q, { bold: true }),
        label('Answer'),
        copy(a),
      ]),

      // ── 10. FOOTER ──
      section(10, 'Footer'),
      space(),
      label('Tagline'),
      copy('Breaking the silence and stigma of sexual abuse. Pursuing justice and healing for survivors across Jewish communities in Israel and beyond.'),
      space(),
      label('Contact'),
      copy('02-372-4073   ·   support@magen-israel.org   ·   www.magen-israel.org'),
      space(),
      label('Copyright'),
      copy('© 2025 Magen for Jewish Communities. Registered nonprofit. All rights reserved.'),
      space(),
      label('FAQ micro-CTA'),
      copy('If you\'re unsure where to start, you can reach out by phone, WhatsApp, or email. You don\'t need to have everything figured out — you can just begin.'),
      label('Button'),
      copy('Reach out to Magen →'),

    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/sessions/dazzling-ecstatic-ride/magen-copy-review.docx', buffer);
  console.log('Done.');
}).catch(err => console.error(err.message));
