"use client";
import { useState, useEffect } from "react";
import { getAccessToken, clearTokens } from "@/lib/auth";

export function useAuth() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(getAccessToken() !== null);
  }, []);

  function logout() {
    clearTokens();
    setIsLoggedIn(false);
  }

  return { isLoggedIn, logout };
}
