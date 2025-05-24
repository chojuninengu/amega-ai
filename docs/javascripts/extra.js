// Custom JavaScript for Amega AI Documentation

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add copy button success animation
    document.querySelectorAll('.md-clipboard').forEach(button => {
        button.addEventListener('click', function() {
            const originalTitle = this.title;
            this.title = 'Copied!';
            setTimeout(() => {
                this.title = originalTitle;
            }, 1500);
        });
    });

    // Add external link icons
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        if (!link.hostname.includes('amega-ai')) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener');
            if (!link.classList.contains('md-social__link')) {
                const icon = document.createElement('span');
                icon.classList.add('external-link-icon');
                icon.innerHTML = ' ↗';
                link.appendChild(icon);
            }
        }
    });

    // Add table of contents highlighting
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const id = entry.target.getAttribute('id');
            if (entry.intersectionRatio > 0) {
                document.querySelector(`nav.md-nav a[href="#${id}"]`)?.classList.add('active');
            } else {
                document.querySelector(`nav.md-nav a[href="#${id}"]`)?.classList.remove('active');
            }
        });
    });

    // Track all section headings
    document.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]').forEach((section) => {
        observer.observe(section);
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Press '/' to focus search
        if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            document.querySelector('.md-search__input').focus();
        }
        
        // Press 'Esc' to close search
        if (e.key === 'Escape') {
            document.querySelector('.md-search__input').blur();
        }
    });
}); 