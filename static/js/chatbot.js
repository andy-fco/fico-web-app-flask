document.addEventListener("DOMContentLoaded", () => {
    const widget = document.getElementById("chatbot-widget");
    const toggleButton = document.getElementById("chatbot-toggle");
    const closeButton = document.getElementById("chatbot-close");
    const clearButton = document.getElementById("chatbot-clear");
    const panel = document.getElementById("chatbot-panel");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const messages = document.getElementById("chatbot-messages");
    const sendButton = document.getElementById("chatbot-send");

    if (!widget || !toggleButton || !panel || !form || !input || !messages || !sendButton) {
        return;
    }

    function openChat() {
        panel.classList.remove("hidden");
        toggleButton.classList.add("hidden");
        input.focus();
    }

    function closeChat() {
        panel.classList.add("hidden");
        toggleButton.classList.remove("hidden");
    }

    function clearMessagesContainer() {
        messages.innerHTML = "";
    }

    function addWelcomeMessage() {
        addMessage(
            "Hola, soy el asistente de FiCo. Puedo ayudarte a analizar tus movimientos, presupuestos, objetivos y simulaciones.",
            "assistant"
        );
    }

    function addMessage(content, role) {
        const bubble = document.createElement("div");

        const baseClasses = [
            "w-fit",
            "max-w-[82%]",
            "rounded-2xl",
            "border",
            "px-4",
            "py-3",
            "text-sm",
            "shadow-md",
            "whitespace-pre-wrap",
        ];

        if (role === "user") {
            bubble.classList.add(
                ...baseClasses,
                "ml-auto",
                "rounded-br-sm",
                "border-[var(--color-brand-secondary)]",
                "bg-[var(--color-brand-primary)]",
                "text-black"
            );
        } else {
            bubble.classList.add(
                ...baseClasses,
                "rounded-bl-sm",
                "border-zinc-700",
                "bg-zinc-800",
                "text-zinc-100"
            );
        }

        bubble.textContent = content;
        messages.appendChild(bubble);
        messages.scrollTop = messages.scrollHeight;
    }

    async function loadHistory() {
        try {
            const response = await fetch("/api/chatbot/history");
            const data = await response.json();

            clearMessagesContainer();

            if (!response.ok || !data.history || data.history.length === 0) {
                addWelcomeMessage();
                return;
            }

            data.history.forEach((item) => {
                addMessage(item.content, item.role);
            });
        } catch (error) {
            clearMessagesContainer();
            addWelcomeMessage();
        }
    }

    async function clearHistory() {
        try {
            await fetch("/api/chatbot/clear", {
                method: "POST",
            });
        } catch (error) {
            console.error(error);
        }

        clearMessagesContainer();
        addWelcomeMessage();
    }

    function setLoading(isLoading) {
        input.disabled = isLoading;
        sendButton.disabled = isLoading;
        sendButton.textContent = isLoading ? "…" : "→";
    }

    toggleButton.addEventListener("click", (event) => {
        event.stopPropagation();
        openChat();
    });

    closeButton.addEventListener("click", closeChat);

    clearButton?.addEventListener("click", (event) => {
        event.stopPropagation();
        clearHistory();
    });

    panel.addEventListener("click", (event) => {
        event.stopPropagation();
    });

    document.addEventListener("click", () => {
        if (!panel.classList.contains("hidden")) {
            closeChat();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const message = input.value.trim();

        if (!message) {
            return;
        }

        addMessage(message, "user");
        input.value = "";
        setLoading(true);

        try {
            const response = await fetch("/api/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();

            if (!response.ok) {
                addMessage(
                    data.error || "Ocurrió un error al consultar el asistente.",
                    "assistant"
                );
                return;
            }

            addMessage(data.response, "assistant");
        } catch (error) {
            addMessage(
                "No se pudo conectar con el asistente.",
                "assistant"
            );
        } finally {
            setLoading(false);
            input.focus();
        }
    });

    loadHistory();
});