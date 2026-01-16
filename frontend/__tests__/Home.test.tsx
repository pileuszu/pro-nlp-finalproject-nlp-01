import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Page from '../src/app/(public)/page'

// MSW는 테스트 환경에서 별도로 설정하거나 Mock 해야 함
// 여기서는 간단히 fetch를 모킹하여 테스트
global.fetch = jest.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve([
            { id: 1, title: 'Test Job', company: 'Test Company', deadline: '2026-01-01', tags: ['Tag'] }
        ]),
    })
) as jest.Mock;

describe('Home Page', () => {
    it('renders heading', async () => {
        const AwaitedPage = await Page; // app router page can be async
        render(<AwaitedPage />)

        const heading = screen.getByRole('heading', { level: 1 })

        expect(heading).toBeInTheDocument()
        expect(heading).toHaveTextContent('채용 공고')
    })
})
