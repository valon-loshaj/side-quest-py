import React, { useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import './TestScrollPage.css';

gsap.registerPlugin(ScrollTrigger);

const TestScrollPage: React.FC = () => {
    useEffect(() => {
        ScrollTrigger.getAll().forEach(trigger => trigger.kill());

        const handleLoad = () => {
            console.log('Window loaded - setting up test animation');

            gsap.timeline({
                scrollTrigger: {
                    trigger: '.wrapper',
                    start: 'top top',
                    end: '+=150%',
                    pin: true,
                    scrub: true,
                    markers: true,
                },
            })
                .to('img', {
                    scale: 2,
                    z: 250,
                    transformOrigin: 'center center',
                    ease: 'power1.inOut',
                })
                .to(
                    '.section.hero',
                    {
                        scale: 1.4,
                        transformOrigin: 'center center',
                        ease: 'power1.inOut',
                    },
                    '<'
                );

            const handleScroll = () => {
                const section = document.querySelector('.section.hero');
                if (!section) return;

                const scrollPos = window.scrollY;
                const wrapperHeight =
                    document.querySelector('.wrapper')?.getBoundingClientRect()
                        .height || 0;
                const opacity = scrollPos / wrapperHeight;

                if (opacity > 0 && opacity < 1) {
                    (section as HTMLElement).style.boxShadow =
                        `10000px 0 0 0 rgba(0, 0, 0, ${opacity}) inset`;
                }
            };

            window.addEventListener('scroll', handleScroll);
        };

        if (document.readyState === 'complete') {
            handleLoad();
        } else {
            window.addEventListener('load', handleLoad);
        }

        return () => {
            window.removeEventListener('load', handleLoad);
            window.removeEventListener('scroll', () => {});
            ScrollTrigger.getAll().forEach(trigger => trigger.kill());
        };
    }, []);

    return (
        <div className="wrapper">
            <div className="intro">
                <h1>The Story of</h1>
                <p>something very spooky</p>
            </div>
            <div className="content">
                <section className="section hero"></section>
                <section className="section gradient-purple"></section>
                <section className="section gradient-blue">
                    <div className="test">
                        <p>In the shadowed depths of yon ancient keep, </p>
                        <p>lurketh secrets darker than the night.</p>
                        <p>
                            Beware, for in the forgotten corners of this cursed realm,
                        </p>
                        <p>doth dwell entities of eldritch horror,</p>
                        <p>
                            their eerie whispers echoing through the corridors like the
                            lamentations of souls long departed.
                        </p>
                    </div>
                </section>
            </div>
            <div className="image-container">
                <img
                    src="https://uploads-ssl.webflow.com/5cff83ac2044e22cb8cf2f11/5d13364599bb70e3560cc4e5_background-min%203.png"
                    alt="background"
                />
            </div>
        </div>
    );
};

export default TestScrollPage;
