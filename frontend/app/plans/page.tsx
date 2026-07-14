"use client";

import { Check, Crown, Sparkles, Users, Zap } from "lucide-react";
import { useToast } from "@/components/Toast";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Try Repurposer with your own API keys.",
    icon: Sparkles,
    accent:
      "bg-surface-sunken text-ink ring-brand-900/10 dark:ring-brand-200/15",
    features: [
      "5 generations per month",
      "All 5 output formats",
      "Bring your own LLM key",
      "Basic quality review",
      "Community support",
    ],
    cta: "Current plan",
    highlighted: false,
    disabled: true,
  },
  {
    id: "pro",
    name: "Pro",
    price: "$19",
    period: "per month",
    description: "For creators who publish every week.",
    icon: Zap,
    accent:
      "bg-brand-50 text-brand-800 ring-brand-300 dark:bg-brand-900/50 dark:text-brand-200 dark:ring-brand-600",
    features: [
      "Unlimited generations",
      "All 5 output formats",
      "Priority LangGraph pipeline",
      "Advanced quality retry",
      "Generation history",
      "Email support",
    ],
    cta: "Upgrade to Pro",
    highlighted: true,
    disabled: false,
  },
  {
    id: "team",
    name: "Team",
    price: "$49",
    period: "per month",
    description: "For agencies and content teams.",
    icon: Users,
    accent:
      "bg-violet-50 text-violet-800 ring-violet-200 dark:bg-violet-950/50 dark:text-violet-200 dark:ring-violet-800",
    features: [
      "Everything in Pro",
      "Up to 5 team members",
      "Shared provider keys",
      "Team workspace",
      "Export all formats",
      "Priority support",
    ],
    cta: "Contact sales",
    highlighted: false,
    disabled: false,
  },
] as const;

export default function PlansPage() {
  const { showToast } = useToast();

  function handleSelect(planName: string) {
    showToast(`${planName} subscriptions coming soon!`, "info");
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-surface-sunken/40">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:py-12">
        {/* Header */}
        <header className="mb-10 text-center">
          <p className="step-label mb-3 justify-center">
            <span className="step-num">
              <Crown className="h-3 w-3" />
            </span>
            Subscription
          </p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Choose your plan
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-sm text-ink-muted sm:text-base">
            Pick a plan that fits your workflow. All plans use your content — we
            never train on your articles.
          </p>
        </header>

        {/* Plan cards */}
        <div className="grid gap-6 lg:grid-cols-3 lg:items-stretch">
          {PLANS.map((plan) => {
            const Icon = plan.icon;
            return (
              <article
                key={plan.id}
                className={`panel relative flex flex-col overflow-hidden transition-all duration-300 hover:shadow-lift ${
                  plan.highlighted
                    ? "ring-2 ring-brand-500/40 dark:ring-brand-400/50 lg:scale-[1.02]"
                    : "hover:-translate-y-0.5"
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-brand-400 via-brand-600 to-brand-400" />
                )}

                <div className="border-b border-brand-900/5 p-6 dark:border-brand-200/10">
                  {plan.highlighted && (
                    <span className="mb-3 inline-flex rounded-full bg-brand-700 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">
                      Most popular
                    </span>
                  )}
                  <div className="flex items-start justify-between gap-3">
                    <div
                      className={`inline-flex rounded-xl p-2.5 ring-1 ring-inset ${plan.accent}`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>
                  <h2 className="mt-4 font-display text-xl font-semibold text-ink">
                    {plan.name}
                  </h2>
                  <p className="mt-1 text-sm text-ink-muted">{plan.description}</p>
                  <div className="mt-5 flex items-baseline gap-1">
                    <span className="font-display text-4xl font-semibold text-ink">
                      {plan.price}
                    </span>
                    <span className="text-sm text-ink-muted">/{plan.period}</span>
                  </div>
                </div>

                <ul className="flex-1 space-y-3 px-6 py-6">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2.5 text-sm">
                      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-900/50">
                        <Check className="h-3 w-3 text-brand-700 dark:text-brand-400" />
                      </span>
                      <span className="text-ink-muted">{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="border-t border-brand-900/5 p-6 dark:border-brand-200/10">
                  <button
                    type="button"
                    onClick={() => !plan.disabled && handleSelect(plan.name)}
                    disabled={plan.disabled}
                    className={
                      plan.highlighted
                        ? "btn-primary w-full"
                        : plan.disabled
                          ? "w-full cursor-default rounded-xl border border-brand-900/10 bg-surface-sunken px-5 py-2.5 text-sm font-semibold text-ink-muted dark:border-brand-200/15"
                          : "w-full rounded-xl border border-brand-900/10 bg-surface-raised px-5 py-2.5 text-sm font-semibold text-ink transition-colors hover:border-brand-400 hover:bg-brand-50 dark:border-brand-200/15 dark:hover:bg-brand-900/40"
                    }
                  >
                    {plan.cta}
                  </button>
                </div>
              </article>
            );
          })}
        </div>

        {/* Footer note */}
        <div className="panel mt-10 p-5 text-center sm:p-6">
          <p className="text-sm text-ink-muted">
            <span className="font-semibold text-ink">Demo pricing</span> — payment
            integration coming soon. You can use Repurposer for free with your own
            LLM API keys today.
          </p>
          <p className="mt-2 text-xs text-ink-soft">
            Cancel anytime · No hidden fees · Secure checkout (coming soon)
          </p>
        </div>
      </div>
    </div>
  );
}
