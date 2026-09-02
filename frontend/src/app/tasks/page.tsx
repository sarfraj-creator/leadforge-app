"use client";

import React, { useState, useEffect } from "react";
import { CheckSquare, Plus, Calendar, Clock, AlertCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface TaskItem {
  id: number;
  lead_id?: number;
  company_name?: string;
  title: string;
  description?: string;
  task_type: string;
  due_date?: string;
  priority: string;
  status: string;
  created_at: string;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newType, setNewType] = useState("Follow-up");
  const [newPriority, setNewPriority] = useState("Medium");
  const [creating, setCreating] = useState(false);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<TaskItem[]>("/crm/tasks");
      setTasks(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const toggleTask = async (id: number) => {
    try {
      const res = await apiFetch<{ status: string }>(`/crm/tasks/${id}/toggle`, { method: "PATCH" });
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? { ...t, status: res.status } : t))
      );
    } catch (err) {
      alert("Failed to toggle task: " + err);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      await apiFetch("/crm/tasks", {
        method: "POST",
        body: JSON.stringify({
          title: newTitle.trim(),
          task_type: newType,
          priority: newPriority,
        })
      });
      setShowModal(false);
      setNewTitle("");
      fetchTasks();
    } catch (err) {
      alert("Failed to create task: " + err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Sales Tasks & Follow-ups</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Action items and scheduled discovery calls for qualified prospects.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-semibold shadow-xs"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Task</span>
        </button>
      </div>

      {/* Task List */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-xs divide-y divide-slate-100 text-xs">
        {loading ? (
          <div className="py-12 text-center text-slate-400">Loading tasks...</div>
        ) : tasks.length === 0 ? (
          <div className="py-12 text-center text-slate-400">No pending tasks found.</div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="p-4 flex items-center justify-between hover:bg-slate-50 transition"
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={task.status === "Completed"}
                  onChange={() => toggleTask(task.id)}
                  className="mt-0.5 rounded border-slate-300 text-blue-600 focus:ring-0 cursor-pointer"
                />
                <div>
                  <div className={`font-bold ${task.status === "Completed" ? "line-through text-slate-400" : "text-slate-900"}`}>
                    {task.title}
                  </div>
                  {task.description && (
                    <div className="text-[11px] text-slate-500 mt-0.5">{task.description}</div>
                  )}
                  {task.company_name && (
                    <div className="text-[11px] text-blue-600 font-medium mt-0.5">
                      Related: {task.company_name}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                  {task.task_type}
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  task.priority === "High" ? "bg-rose-100 text-rose-800" : "bg-blue-50 text-blue-800"
                }`}>
                  {task.priority}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Task Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="w-full max-w-md bg-white rounded-lg shadow-xl border border-slate-200 p-6 space-y-4 text-xs">
            <h2 className="font-bold text-sm text-slate-900">Create Follow-up Task</h2>
            <form onSubmit={handleCreateTask} className="space-y-3">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Task Title:</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Schedule discovery call with owner"
                  className="w-full px-3 py-1.5 rounded border border-slate-300 outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-600 font-medium mb-1">Type:</label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded border border-slate-300 bg-white outline-none"
                  >
                    <option value="Call">Call</option>
                    <option value="Email">Email</option>
                    <option value="Meeting">Meeting</option>
                    <option value="Follow-up">Follow-up</option>
                    <option value="Proposal">Proposal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-600 font-medium mb-1">Priority:</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full px-2.5 py-1.5 rounded border border-slate-300 bg-white outline-none"
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 text-slate-600 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-1.5 bg-blue-600 text-white font-semibold rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  {creating ? "Saving..." : "Save Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
