import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppSelector } from '../store';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from '../styles/LandingPage.module.css';
import { scrollToNextPage } from '../services/scroll-navigation';

gsap.registerPlugin(ScrollTrigger);

const LandingPage: React.FC = () => {
    const { isAuthenticated } = useAppSelector(state => state.auth);
    const navigate = useNavigate();

    const navigateToNextPage = () => {
        try {
            scrollToNextPage(navigate, isAuthenticated);
        } catch (error) {
            console.error('Navigation error:', error);
        }
    };

    useEffect(() => {
        if (document.readyState === 'complete') {
            initGSAP();
        } else {
            window.addEventListener('load', initGSAP);
        }

        return () => {
            window.removeEventListener('load', initGSAP);
            ScrollTrigger.getAll().forEach(st => st.kill());
            gsap.killTweensOf('*');
        };
    }, []);

    function initGSAP() {
        ScrollTrigger.getAll().forEach(trigger => trigger.kill());

        const wrapper = document.querySelector(`.${styles.wrapper}`);
        const tunnelImage = document.querySelector(`.${styles.tunnelImage}`);
        const heroSection = document.querySelector(`.${styles.heroSection}`);

        if (!wrapper || !tunnelImage || !heroSection) {
            console.error('Required elements not found');
            return;
        }

        gsap.timeline({
            scrollTrigger: {
                trigger: wrapper,
                start: 'top top',
                end: '+=200%',
                pin: true,
                scrub: true,
                markers: true,
            },
        })
            .to(tunnelImage, {
                scale: 3,
                z: 500,
                transformOrigin: 'center center',
                ease: 'power1.inOut',
            })
            .to(
                heroSection,
                {
                    scale: 1.5,
                    transformOrigin: 'center center',
                    ease: 'power1.inOut',
                },
                '<'
            );

        window.addEventListener('scroll', () => {
            const darkOverlay = document.querySelector(`.${styles.darkOverlay}`);
            if (!wrapper || !darkOverlay) return;

            const scrollPos = window.scrollY;
            const wrapperHeight = wrapper.getBoundingClientRect().height;
            const progress = Math.min(0.7, scrollPos / (wrapperHeight / 3));

            (darkOverlay as HTMLElement).style.backgroundColor =
                `rgba(0, 0, 0, ${0.3 + progress * 0.6})`;
        });
    }

    return (
        <div className={styles.wrapper}>
            <div className={styles.darkOverlay}></div>

            <div className={styles.intro}>
                <h1>Side Quest</h1>
                <p
                    className={styles.adventureLink}
                    onClick={navigateToNextPage}
                    role="button"
                    tabIndex={0}
                    onKeyDown={e => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            navigateToNextPage();
                        }
                    }}
                >
                    Begin Your Adventure
                </p>
            </div>

            <div className={styles.content}>
                <section
                    className={`${styles.section} ${styles.heroSection}`}
                ></section>
                <section
                    className={`${styles.section} ${styles.gradientPurple}`}
                ></section>
                <section className={`${styles.section} ${styles.gradientBlue}`}>
                    <div className={styles.questDescription}>
                        <p>Embark on a journey of epic quests and legendary rewards.</p>
                        <p>
                            Track your adventures, conquer challenges, and level up your
                            character.
                        </p>
                        <p>Scroll down to continue your quest...</p>
                        <div className={styles.scrollIndicator}>
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </section>
            </div>

            <div className={styles.imageContainer}>
                <img
                    src="/images/side-quest-tunnel-image.png"
                    alt="Medieval tunnel entrance"
                    className={styles.tunnelImage}
                />
            </div>
        </div>
    );
};

export default LandingPage;
