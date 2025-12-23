import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-gray-200", className)}
      {...props}
    />
  );
}

export function SOAPSkeleton() {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border p-4">
        <Skeleton className="h-6 w-32 mb-3" />
        <Skeleton className="h-20 w-full" />
      </div>
      <div className="rounded-lg border p-4">
        <Skeleton className="h-6 w-32 mb-3" />
        <Skeleton className="h-20 w-full" />
      </div>
      <div className="rounded-lg border p-4">
        <Skeleton className="h-6 w-32 mb-3" />
        <Skeleton className="h-20 w-full" />
      </div>
      <div className="rounded-lg border p-4">
        <Skeleton className="h-6 w-32 mb-3" />
        <Skeleton className="h-20 w-full" />
      </div>
    </div>
  );
}
