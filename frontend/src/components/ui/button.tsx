import Link from "next/link";
import type { MouseEventHandler, ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "outline" | "danger" | "ghost";

interface ButtonProps {
  children: ReactNode;
  variant?: ButtonVariant;
  href?: string;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  loading?: boolean;
  loadingText?: string;
  className?: string;
  onClick?: MouseEventHandler<HTMLButtonElement>;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "border-[var(--color-text-primary)] bg-[var(--color-text-primary)] text-white hover:bg-black",
  secondary: "border-[var(--color-accent)] bg-[var(--color-accent)] text-white hover:brightness-95",
  outline: "border-[var(--color-border-strong)] bg-white text-[var(--color-text-primary)] hover:bg-[var(--color-panel-subtle)]",
  danger: "border-[var(--color-critical)] bg-[var(--color-critical)] text-white hover:brightness-95",
  ghost: "border-transparent bg-transparent text-[var(--color-text-secondary)] hover:bg-[var(--color-panel-subtle)]",
};

export function Button({ children, variant = "primary", href, type = "button", disabled = false, loading = false, loadingText = "Working...", className = "", onClick }: ButtonProps) {
  const unavailable = disabled || loading;
  const classes = `inline-flex min-h-10 items-center justify-center rounded-md border px-4 text-sm font-semibold transition-colors focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-focus-ring)] ${variantClasses[variant]} ${unavailable ? "cursor-not-allowed opacity-55" : ""} ${className}`;
  const content = loading ? loadingText : children;

  if (href && !unavailable) {
    return <Link href={href} className={classes}>{content}</Link>;
  }

  if (href) {
    return <span className={classes} aria-disabled="true">{content}</span>;
  }

  return <button type={type} disabled={unavailable} aria-busy={loading || undefined} className={classes} onClick={onClick}>{content}</button>;
}
