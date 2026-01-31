"use client";

import { useEffect, useState, useCallback } from "react";
import { useToast } from "@/components/ui/toast-context";
import { useAuthStore } from "@/stores/useAuthStore";

export interface Notification {
    id: number;
    title: string;
    message: string;
    is_read: boolean;
    link?: string;
    created_at: string;
}

export function useNotifications() {
    const { isAuthenticated, token } = useAuthStore();
    const { toast } = useToast();
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [unreadCount, setUnreadCount] = useState(0);

    const fetchNotifications = useCallback(async () => {
        if (!isAuthenticated) return;
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/notifications`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (res.ok) {
                const data = await res.json();
                setNotifications(data.items);
                setUnreadCount(data.unread_count);
            }
        } catch (err) {
            console.error("Failed to fetch notifications", err);
        }
    }, [isAuthenticated, token]);

    const markAsRead = async (id: number) => {
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/notifications/${id}/read`, {
                method: "PATCH",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (res.ok) {
                setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
                setUnreadCount(prev => Math.max(0, prev - 1));
            }
        } catch (err) {
            console.error("Failed to mark notification as read", err);
        }
    };

    useEffect(() => {
        if (!isAuthenticated) return;

        // Initialize
        const init = async () => {
            await fetchNotifications();
        };
        init();

        // SSE Setup
        const url = `${process.env.NEXT_PUBLIC_API_URL || ""}/api/notifications/events?token=${token}`;
        // Note: EventSource doesn't support headers natively, so we pass token as query param
        const eventSource = new EventSource(url);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Show Toast using our custom useToast
            toast(data.message || data.title, "success");

            // Refresh list
            fetchNotifications();
        };

        eventSource.onerror = (err) => {
            console.error("SSE Error:", err);
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, [isAuthenticated, token, fetchNotifications, toast]);

    return { notifications, unreadCount, markAsRead, refresh: fetchNotifications };
}
