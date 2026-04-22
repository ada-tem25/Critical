const Footer = () => {
  return (
    <footer className="w-full px-6 py-4 border-t border-border">
      <div className="max-w-5xl mx-auto flex items-center justify-end gap-2">
        {["Mentions légales", "Politique de confidentialité", "Contact", "À propos"].map(item => (
          <button
            key={item}
            type="button"
            className="font-ui text-xs text-muted-foreground transition-colors duration-150 hover:text-muted-foreground/50 active:text-foreground cursor-pointer select-none bg-transparent border-none p-0"
          >
            {item}
          </button>
        ))}
      </div>
    </footer>
  );
};
export default Footer;