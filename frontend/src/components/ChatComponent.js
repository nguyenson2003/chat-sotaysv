import React, { useState, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import Markdown from 'markdown-to-jsx'

// Chỉ định worker cho react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();


const ChatComponent = () => {
  const [numPages, setNumPages] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const pageRefs = useRef([]);

  // Đường dẫn tới file PDF trong thư mục `public`
  const pdfFile = 'Sổ tay sinh viên K65 - 2024.pdf';

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }
  const scrollToPage = (pageNumber) => {
    const pageElement = pageRefs.current[pageNumber - 1];
    if (pageElement) {
      pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };
  const ScorllButton = ({ page }) => <button key={page} onClick={() => scrollToPage(page)}>[{page}]</button>

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt: input }),
        headers: { 'Content-Type': 'application/json' },
      }).then(res => res.json());
      const text = response.text;

      const botMessage = { sender: 'bot', text: text };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error("Error calling Gemini API:", error);
      const errorMessage = { sender: 'bot', text: 'Xin lỗi, đã có lỗi xảy ra.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <div className="chat-container">
      {/* Khung Chat bên trái */}
      <div className="chat-window">
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender}`}>
              <Markdown
                options={{
                  overrides: {
                    ScorllButton: {
                      component: ScorllButton,
                    },
                  },
                }}
              >{msg.text}</Markdown>
            </div>
          ))}
          {isLoading && <div className="message bot"><p>Đang suy nghĩ...</p></div>}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={input}
            disabled={isLoading}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Nhập câu hỏi của bạn..."
          />
          <button onClick={handleSendMessage}>Gửi</button>
        </div>
      </div>

      {/* Khung PDF bên phải */}
      <div className="pdf-viewer">
        <Document file={pdfFile} onLoadSuccess={onDocumentLoadSuccess}>
          {Array.from(new Array(numPages), (el, index) => (
            <div ref={el => pageRefs.current[index] = el}>
              <Page key={`page_${index + 1}`} pageNumber={index + 1} />
            </div>
          ))}
        </Document>
      </div>
    </div>
  );
};

export default ChatComponent;
