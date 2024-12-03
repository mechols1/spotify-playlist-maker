export default function Layout({ children }) {
    return (
      <div className="min-h-screen bg-gray-100">
        <main>{children}</main>
      </div>
    );
  }