// The old "Explore" starter screen was replaced by Settings ("My courses").
// This file just forwards any old links there. You can delete it.
import { Redirect } from 'expo-router';

export default function ExploreRedirect() {
  return <Redirect href="/settings" />;
}
