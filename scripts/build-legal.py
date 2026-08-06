# -*- coding: utf-8 -*-
"""Generate the legal pages from the shared site shell.

Terms and Privacy reuse contact.html's head, age gate, nav and footer so they
never drift from the rest of the site. Only the <main> block differs. Re-run
after changing the shell:

    python scripts/build-legal.py
"""

import io
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EFFECTIVE = "31 July 2026"
EMAIL = "sales@bargainalternatives.com"
DOMAIN = "www.bargainalternatives.com"


def shell():
    src = io.open(os.path.join(HERE, "contact.html"), encoding="utf-8").read()
    lines = src.split("\n")
    i_main = next(i for i, l in enumerate(lines) if l.strip() == '<main id="main">')
    i_end = next(i for i, l in enumerate(lines) if l.strip() == "</main>")
    return "\n".join(lines[:i_main]), "\n".join(lines[i_end:])


def page(slug, title, desc, eyebrow, h1_lines, body):
    head, tail = shell()

    lines_html = "\n".join(
        '      <span class="line"><span data-hero-line%s>%s</span></span>'
        % (' class="gradient-text"' if i == len(h1_lines) - 1 else "", t)
        for i, t in enumerate(h1_lines)
    )

    main = '''<main id="main">

<section class="page-head">
  <div class="container">
    <span class="eyebrow" data-hero-fade>%s</span>
    <h1 class="page-head__title" style="margin-bottom:var(--space-3)">
%s
    </h1>
    <p class="lede" data-hero-fade>Last updated %s</p>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="legal reveal">
%s
    </div>
  </div>
</section>

''' % (eyebrow, lines_html, EFFECTIVE, body)

    out = head + "\n" + main + tail
    out = out.replace("<title>Wholesale Inquiry — Bargain Vape</title>",
                      "<title>%s — Bargain Vape</title>" % title)
    out = re.sub(r'<meta name="description" content="[^"]*">',
                 '<meta name="description" content="%s">' % desc, out, count=1)
    out = re.sub(r'<link rel="canonical" href="[^"]*">',
                 '<link rel="canonical" href="https://%s/%s">' % (DOMAIN, slug), out, count=1)
    out = re.sub(r'<meta property="og:url" content="[^"]*">',
                 '<meta property="og:url" content="https://%s/%s">' % (DOMAIN, slug), out, count=1)
    out = re.sub(r'<meta property="og:title" content="[^"]*">',
                 '<meta property="og:title" content="%s — Bargain Vape">' % title, out, count=1)
    out = re.sub(r'<meta property="og:description" content="[^"]*">',
                 '<meta property="og:description" content="%s">' % desc, out, count=1)
    out = out.replace(' aria-current="page"', '')
    out = out.replace('href="#wholesale-form"', 'href="contact.html"')

    io.open(os.path.join(HERE, slug), "w", encoding="utf-8").write(out)
    print("wrote", slug)


# --------------------------------------------------------------------- TERMS

TERMS = '''      <h2>1. Who we are</h2>
      <p>
        This website is operated by Bargain Vape ("Bargain Vape", "we", "us", "our"). By accessing
        or using the site you agree to these Terms of Service. If you do not agree, please do not
        use the site.
      </p>

      <h2>2. You must be 21 or older</h2>
      <p>
        This site presents information about hemp-derived THC products and is intended only for
        adults aged 21 and over, and for licensed retail buyers evaluating our products for resale.
        By entering the site you represent that you are at least 21 years of age and of legal age
        to view this content in your jurisdiction. We reserve the right to refuse service to anyone
        we reasonably believe does not meet these requirements.
      </p>

      <h2>3. This site is not a store</h2>
      <p>
        Bargain Vape sells to retail businesses only. This website does not sell products, take
        payment, or fulfil consumer orders. Nothing on this site is an offer to sell to consumers.
        Product images, descriptions, display box configurations and the price printed on packaging are
        provided for informational purposes and may change without notice.
      </p>
      <p>
        A wholesale inquiry submitted through this site is a request for information. It does not
        create a binding order, reserve stock, or guarantee pricing or availability. Any sale is
        subject to a separate written agreement between Bargain Vape and the purchasing business.
      </p>

      <h2>4. Product and legal information</h2>
      <p>
        Our products are derived from hemp containing no more than 0.3%% Delta-9 THC on a dry weight
        basis, as defined by the Agriculture Improvement Act of 2018 (the "2018 Farm Bill").
        Statements on this site have not been evaluated by the Food and Drug Administration. These
        products are not intended to diagnose, treat, cure or prevent any disease.
      </p>
      <p>
        Hemp-derived THC products are regulated differently from state to state and some
        jurisdictions restrict or prohibit them entirely. It is the buyer's responsibility to
        confirm that these products may lawfully be purchased, stocked and resold in their
        jurisdiction. We make no representation that these products are lawful in any particular
        location.
      </p>

      <h2>5. Acceptable use</h2>
      <p>You agree not to:</p>
      <ul>
        <li>use the site for any unlawful purpose, or in violation of any applicable regulation;</li>
        <li>misrepresent your age, identity, or your business's licensing status;</li>
        <li>attempt to gain unauthorised access to the site or any related system;</li>
        <li>use automated means to scrape, harvest or overload the site;</li>
        <li>copy, reproduce or redistribute site content except as permitted below.</li>
      </ul>

      <h2>6. Intellectual property</h2>
      <p>
        The Bargain Vape name, logo, packaging design, product photography, and the text and layout
        of this site are owned by Bargain Vape or its licensors and are protected by intellectual
        property law. Retailers who stock our products may use our product photography and brand
        assets for the purpose of marketing those products, provided the assets are not altered,
        recoloured or used in a way that misrepresents the brand. All other use requires our written
        permission.
      </p>

      <h2>7. Third-party links</h2>
      <p>
        The site may link to third-party websites. We do not control those sites and are not
        responsible for their content, products or privacy practices.
      </p>

      <h2>8. Disclaimer of warranties</h2>
      <p>
        The site is provided "as is" and "as available" without warranties of any kind, whether
        express or implied, including but not limited to implied warranties of merchantability,
        fitness for a particular purpose, and non-infringement. We do not warrant that the site will
        be uninterrupted, error-free, or that information on it is complete or current.
      </p>

      <h2>9. Limitation of liability</h2>
      <p>
        To the fullest extent permitted by law, Bargain Vape shall not be liable for any indirect,
        incidental, special, consequential or punitive damages, or any loss of profits or revenue,
        arising out of your use of, or inability to use, this site.
      </p>

      <h2>10. Indemnity</h2>
      <p>
        You agree to indemnify and hold harmless Bargain Vape and its officers, employees and agents
        from any claim or demand arising out of your use of the site or your breach of these Terms.
      </p>

      <h2>11. Changes to these terms</h2>
      <p>
        We may update these Terms from time to time. The "last updated" date at the top of this page
        reflects the most recent revision. Continued use of the site after a change constitutes
        acceptance of the revised Terms.
      </p>

      <h2>12. Governing law</h2>
      <p>
        These Terms are governed by the laws of the State of Florida, without regard to its conflict
        of law provisions.
        <!-- LEGAL REVIEW: confirm the correct governing state and whether an arbitration or venue
             clause should be added. -->
      </p>

      <h2>13. Contact</h2>
      <p>
        Questions about these Terms can be sent to
        <a href="mailto:%s">%s</a>. Email is our only channel for these enquiries.
      </p>''' % (EMAIL, EMAIL)


# ------------------------------------------------------------------- PRIVACY

PRIVACY = '''      <h2>1. Overview</h2>
      <p>
        This policy explains what information Bargain Vape collects through
        <span class="nowrap">%s</span>, why we collect it, and what we do with it. We have
        deliberately kept the site's data collection minimal.
      </p>

      <h2>2. What we collect</h2>
      <h3>Information you give us</h3>
      <p>
        If you submit a wholesale inquiry, we collect what you type into that form: your business
        name, contact name, email address, phone number, city and state, business type, the display box
        quantities you are interested in, and any message you write. We ask for this only so we can
        respond to your inquiry.
      </p>
      <h3>Information collected automatically</h3>
      <p>
        Our host records standard server access data such as IP address, browser type and pages
        requested. This is used for security and to keep the site running. We do not run analytics,
        advertising trackers, or third-party marketing pixels on this site.
      </p>
      <h3>Cookies and local storage</h3>
      <p>
        We do not use advertising or analytics cookies. The site stores a single value in your
        browser's session storage to remember that you confirmed your age, so you are not asked
        again on every page. It is cleared when you close the browser and is never sent to us.
      </p>

      <h2>3. How we use it</h2>
      <ul>
        <li>To respond to your wholesale inquiry and to correspond with you about it.</li>
        <li>To assess whether a prospective stockist is a fit for our products.</li>
        <li>To keep the site secure and working.</li>
        <li>To meet legal or regulatory obligations, including age-restriction requirements.</li>
      </ul>
      <p>We do not sell, rent or trade your personal information.</p>

      <h2>4. Who else sees it</h2>
      <p>
        Form submissions are processed and stored by our website host, Netlify, which acts as a
        service provider on our behalf, and are delivered to our business email. We may also share
        information where required by law, or to protect our legal rights. Beyond that, we do not
        share your information with third parties.
      </p>

      <h2>5. How long we keep it</h2>
      <p>
        We keep wholesale inquiries for as long as needed to evaluate and service the business
        relationship, and afterwards only as long as required for our records or by law. You can ask
        us to delete your inquiry at any time.
      </p>

      <h2>6. Your choices and rights</h2>
      <p>
        You can ask us to confirm what information we hold about you, to correct it, or to delete
        it. Write to <a href="mailto:%s">%s</a> and we will respond within a reasonable period.
        Depending on where you live you may have additional rights under state privacy law; tell us
        which state you are writing from and we will treat your request accordingly.
      </p>
      <p>
        Because we do not send marketing email from this site, there is no marketing list to
        unsubscribe from. If that ever changes, every message will carry an unsubscribe link.
      </p>

      <h2>7. Children</h2>
      <p>
        This site is restricted to adults aged 21 and over. We do not knowingly collect information
        from anyone under 21. If you believe a minor has submitted information to us, contact us and
        we will delete it.
      </p>

      <h2>8. Security</h2>
      <p>
        The site is served over HTTPS and form submissions are transmitted encrypted. No method of
        transmission or storage is completely secure, and we cannot guarantee absolute security.
      </p>

      <h2>9. Changes to this policy</h2>
      <p>
        We may update this policy from time to time. The "last updated" date at the top of this page
        reflects the most recent revision.
      </p>

      <h2>10. Contact</h2>
      <p>
        Privacy questions and requests go to <a href="mailto:%s">%s</a>. Email is our only channel
        for these enquiries.
      </p>''' % (DOMAIN, EMAIL, EMAIL, EMAIL, EMAIL)


ACCESSIBILITY = '''      <h2>Our commitment</h2>
      <p>
        We want this site to be usable by everyone, including people who browse with a screen
        reader, navigate by keyboard, enlarge text, or prefer reduced motion. We aim to meet the
        Web Content Accessibility Guidelines (WCAG) 2.1 at Level AA.
      </p>

      <h2>What we have done</h2>
      <ul>
        <li>Text and background colours are tested to meet the WCAG AA contrast minimums.</li>
        <li>Every page can be operated by keyboard alone, with a visible focus outline, and a
            "skip to main content" link at the top.</li>
        <li>Pages use proper landmarks and a logical heading order so screen readers can navigate
            by structure.</li>
        <li>All meaningful images carry descriptive alternative text; decorative images are hidden
            from assistive technology.</li>
        <li>Form fields have visible labels, errors are announced and tied to the field they
            describe, and the first field with a problem receives focus.</li>
        <li>The site honours the "reduce motion" setting in your operating system: animation and
            the background video are turned off when that preference is set.</li>
        <li>Layout is responsive, does not scroll sideways, and remains usable when text is
            enlarged.</li>
        <li>Interactive controls meet the recommended minimum touch target size.</li>
      </ul>

      <h2>Known limitations</h2>
      <p>
        Product packaging photography reproduces artwork that includes stylised neon lettering. The
        information in those images — flavour, strain type, quantity and price — is also given in
        text next to every image, so nothing is available only inside a picture.
      </p>

      <h2>Tell us if something does not work</h2>
      <p>
        If you hit a barrier on this site, we want to hear about it and we will try to fix it.
        Email <a href="mailto:%s">%s</a> and, if you can, tell us the page address, what you were
        trying to do, and the browser or assistive technology you were using. Email is our only
        contact channel, and we aim to respond within five business days.
      </p>

      <h2>Assessment</h2>
      <p>
        This site was evaluated during development by manual review and automated checks covering
        colour contrast, heading structure, landmarks, alternative text, keyboard operation and
        form semantics. It has not been audited by an independent third party.
      </p>''' % (EMAIL, EMAIL)


page("accessibility.html", "Accessibility",
     "Accessibility statement for the Bargain Vape website, our WCAG 2.1 AA commitment, and how to report a barrier.",
     "Legal", ["Accessibility", "statement."], ACCESSIBILITY)

page("terms.html", "Terms of Service",
     "Terms of Service for the Bargain Vape website. Wholesale only, 21+, hemp-derived THC compliance and site use terms.",
     "Legal", ["Terms of", "Service."], TERMS)

page("privacy.html", "Privacy Policy",
     "Privacy Policy for the Bargain Vape website. What we collect through the wholesale inquiry form, why, and your choices.",
     "Legal", ["Privacy", "Policy."], PRIVACY)
