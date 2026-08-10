'use client';
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle2, Layout, Zap, Shield, Globe, Users } from 'lucide-react';

export default function LandingPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-emerald-500/30 overflow-hidden relative font-sans">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-emerald-600/20 blur-[120px] mix-blend-screen" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-teal-600/20 blur-[120px] mix-blend-screen" />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-slate-950/50 backdrop-blur-md">
        <div className="container mx-auto px-6 h-20 flex items-center justify-between">
          <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">
            NexusProject
          </div>
          <div className="hidden md:flex gap-8 text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#preview" className="hover:text-white transition">3D Workspace</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
          </div>
          <div className="flex gap-4">
            <Link href="/login" className="px-5 py-2.5 text-sm font-medium hover:text-emerald-400 transition">Log In</Link>
            <Link href="/register" className="px-5 py-2.5 text-sm font-medium bg-emerald-600 hover:bg-emerald-500 rounded-full transition shadow-[0_0_20px_rgba(16,185,129,0.35)]">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-48 pb-32 px-6 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-4xl flex flex-col items-center"
        >
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-sm font-medium backdrop-blur-md">
            🚀 The Future of Enterprise Project Management
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
            Manage Everything.<br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400">In Three Dimensions.</span>
          </h1>
          <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
            Unify your team's workflow with an immersive, collaborative workspace that scales from small teams to global enterprises.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center w-full sm:w-auto">
            <Link href="/register" className="flex items-center justify-center gap-2 px-8 py-4 text-lg font-medium bg-emerald-600 hover:bg-emerald-500 rounded-full transition shadow-[0_0_30px_rgba(16,185,129,0.4)] group">
              Start Free Trial <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="#preview" className="flex items-center justify-center px-8 py-4 text-lg font-medium border border-white/10 hover:bg-white/5 rounded-full transition backdrop-blur-sm">
              See How It Works
            </Link>
          </div>
        </motion.div>
      </section>
      
      {/* 3D Workspace Preview */}
      <section id="preview" className="relative z-10 py-32 px-6">
        <div className="container mx-auto text-center max-w-5xl">
            <h2 className="text-3xl md:text-5xl font-bold mb-8">The 3D Workspace</h2>
            <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto">Visualize dependencies, team structures, and bottlenecks spatially in our revolutionary WebGL environment.</p>
            
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.7 }}
              className="aspect-video rounded-3xl bg-slate-900 border border-emerald-500/20 flex items-center justify-center relative overflow-hidden shadow-2xl group cursor-pointer"
            >
                <div className="absolute inset-0 bg-gradient-to-tr from-emerald-900/40 to-teal-900/10 opacity-50" />
                <div className="z-10 flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center mb-4 border border-white/20 group-hover:scale-110 transition-transform">
                        <Layout className="w-8 h-8 text-emerald-400" />
                    </div>
                    <p className="text-white font-medium text-lg tracking-wide">[Advanced 3D WebGL Workspace Engine]</p>
                    <p className="text-slate-400 text-sm mt-2">To be fully implemented in Part 3</p>
                </div>
            </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative z-10 py-24 px-6 bg-slate-900/30 border-y border-white/5">
        <div className="container mx-auto max-w-6xl">
            <div className="text-center mb-20">
                <h2 className="text-3xl md:text-5xl font-bold mb-6">Enterprise Features</h2>
                <p className="text-xl text-slate-400 max-w-2xl mx-auto">Everything you need to manage complex projects, shipped with performance in mind.</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
                {[
                    { icon: <Zap className="w-6 h-6 text-yellow-400"/>, title: "Realtime Collaboration", desc: "Work together instantly with live typing, presence, and CRDT-powered rich text." },
                    { icon: <Layout className="w-6 h-6 text-emerald-400"/>, title: "Advanced Workflows", desc: "Build custom Kanban boards, Gantt charts, and complex automation rules." },
                    { icon: <Shield className="w-6 h-6 text-teal-400"/>, title: "Bank-Grade Security", desc: "Role-Based Access Control, audit logs, and strict multi-tenant isolation." },
                    { icon: <Globe className="w-6 h-6 text-cyan-400"/>, title: "Global CDN", desc: "Edge-cached delivery ensures blazing fast load times anywhere in the world." },
                    { icon: <Users className="w-6 h-6 text-emerald-400"/>, title: "Team Management", desc: "Organize members into teams, assign granular permissions, and track activity." },
                    { icon: <CheckCircle2 className="w-6 h-6 text-green-400"/>, title: "Automations", desc: "Reduce busywork with triggers, actions, and custom webhooks." }
                ].map((feature, i) => (
                    <motion.div 
                        key={i} 
                        whileHover={{ y: -5 }} 
                        className="p-8 rounded-2xl bg-slate-800/40 border border-white/5 backdrop-blur-lg hover:bg-slate-800/60 transition-colors"
                    >
                        <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-6 border border-white/5">
                            {feature.icon}
                        </div>
                        <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
                        <p className="text-slate-400 leading-relaxed">{feature.desc}</p>
                    </motion.div>
                ))}
            </div>
        </div>
      </section>
      
      {/* Pricing */}
      <section id="pricing" className="relative z-10 py-32 px-6">
        <div className="container mx-auto max-w-6xl text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Simple, Transparent Pricing</h2>
            <p className="text-xl text-slate-400 mb-16">Start for free, scale when you need to.</p>
            
            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                {[
                    { name: "Starter", price: "$0", desc: "Perfect for small teams", features: ["Up to 10 members", "Unlimited tasks", "Basic Kanban boards", "Community support"] },
                    { name: "Business", price: "$15", desc: "For scaling organizations", features: ["Unlimited members", "3D Workspace access", "Advanced automations", "Priority support"], popular: true },
                    { name: "Enterprise", price: "Custom", desc: "For security-focused orgs", features: ["Dedicated success manager", "SAML SSO", "Audit logging", "99.99% Uptime SLA"] }
                ].map((tier, i) => (
                    <div key={i} className={`p-8 rounded-3xl border ${tier.popular ? 'border-emerald-500 bg-emerald-900/10' : 'border-white/10 bg-slate-900/50'} backdrop-blur-md flex flex-col text-left relative overflow-hidden`}>
                        {tier.popular && <div className="absolute top-0 right-0 bg-emerald-500 text-white text-xs font-bold px-4 py-1 rounded-bl-xl">MOST POPULAR</div>}
                        <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                        <p className="text-slate-400 mb-6">{tier.desc}</p>
                        <div className="text-4xl font-bold mb-8">{tier.price}<span className="text-lg text-slate-500 font-normal">{tier.price !== "Custom" && "/mo"}</span></div>
                        <ul className="space-y-4 mb-8 flex-1">
                            {tier.features.map((f, j) => (
                                <li key={j} className="flex items-center gap-3 text-slate-300">
                                    <CheckCircle2 className="w-5 h-5 text-emerald-400" /> {f}
                                </li>
                            ))}
                        </ul>
                        <Link href="/register" className={`w-full py-3 rounded-xl text-center font-medium transition ${tier.popular ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-white/10 hover:bg-white/20 text-white'}`}>
                            {tier.price === "Custom" ? "Contact Sales" : "Get Started"}
                        </Link>
                    </div>
                ))}
            </div>
        </div>
      </section>
    </div>
  );
}
