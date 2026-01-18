import { render, screen, waitFor } from '@testing-library/react';
import PortfoliosPage from '@/app/(main)/my/portfolios/page';
import React from 'react';

// Mock framer-motion to avoid animation related issues in tests
jest.mock('framer-motion', () => {
    const React = require('react'); // eslint-disable-line @typescript-eslint/no-require-imports

    interface MockProps {
        children?: React.ReactNode;
        [key: string]: unknown;
    }

    const MockDiv = React.forwardRef(({ children, ...props }: MockProps, ref: React.Ref<HTMLDivElement>) => (
        <div {...props} ref={ref}>{children}</div>
    ));
    MockDiv.displayName = 'MotionDiv';

    return {
        motion: {
            div: MockDiv,
        },
        AnimatePresence: ({ children }: MockProps) => <>{children}</>,
    };
});

describe('PortfoliosPage', () => {
    it('renders the page title and description', () => {
        render(<PortfoliosPage />);
        expect(screen.getByText('내 포트폴리오')).toBeInTheDocument();
        expect(screen.getByText(/등록된 포트폴리오를 관리하고/i)).toBeInTheDocument();
    });

    it('fetches and displays portfolios from the mock API', async () => {
        render(<PortfoliosPage />);

        // Mock data from handlers.ts covers these titles
        await waitFor(() => {
            expect(screen.getByText('나만의 기술 블로그')).toBeInTheDocument();
            expect(screen.getByText('졸업 프로젝트 (PDF)')).toBeInTheDocument();
            expect(screen.getByText('오픈소스 기여 내역')).toBeInTheDocument();
        });
    });

    it('displays the "AI READY" badge for portfolios with content', async () => {
        render(<PortfoliosPage />);

        await waitFor(() => {
            const badges = screen.getAllByText(/AI READY/i);
            expect(badges.length).toBeGreaterThan(0);
        });
    });
});
