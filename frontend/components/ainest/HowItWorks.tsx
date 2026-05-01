"use client";

import { motion } from "framer-motion";

const features = [
  {
    title: "Job Discovery",
    description: "Scan thousands of listings effortlessly, no more tedious manual searches on LinkedIn or Indeed.",
    number: "01"
  },
  {
    title: "Smart Cover Letters",
    description: "Automatically generate tailored cover letters and resumes mapped perfectly to the description.",
    number: "02"
  },
  {
    title: "Autopilot Application",
    description: "Submit applications instantly the moment you log in, accelerating your path to the interview.",
    number: "03"
  }
];

export function HowItWorks() {
  return (
    <section className="bg-[#050505] py-32 px-6 relative z-10 border-b border-zinc-900/50 overflow-hidden">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row gap-20">
        
        {/* Left Heavy Column */}
        <div className="flex-1">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="sticky top-32"
          >
            <h2 className="text-4xl font-medium tracking-tight text-white mb-6">
              How it works
            </h2>
            <p className="text-[#a1a1aa] text-lg leading-relaxed max-w-sm">
              Unleash unparalleled efficiency as Applivo transforms the mundane task of job hunting into an extraordinary automated journey.
            </p>
          </motion.div>
        </div>

        {/* Right Feature List */}
        <div className="flex-[1.2] flex flex-col gap-12">
          {features.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: i * 0.15 }}
              className="flex gap-6 group"
            >
              <div className="text-sm font-semibold text-zinc-600 mt-1">{item.number}</div>
              <div>
                <h3 className="text-xl font-medium text-white mb-3 group-hover:text-[#2563eb] transition-colors">
                  {item.title}
                </h3>
                <p className="text-[#a1a1aa] leading-relaxed text-[15px] max-w-sm">
                  {item.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
