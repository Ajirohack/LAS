import { cn } from "@/lib/utils"

function Skeleton({
    className,
    ...props
}: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div
            className={cn("animate-pulse rounded-md bg-zinc-800/50", className)}
            {...props}
        />
    )
}

export { Skeleton }

export function ChatSkeleton() {
    return (
        <div className="flex flex-col gap-4 p-4 max-w-3xl mx-auto w-full">
            <div className="flex gap-4 items-start">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                </div>
            </div>
            <div className="flex gap-4 items-start flex-row-reverse">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="space-y-2 flex-1 flex flex-col items-end">
                    <Skeleton className="h-4 w-[300px]" />
                    <Skeleton className="h-4 w-[250px]" />
                </div>
            </div>
            <div className="flex gap-4 items-start">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-[280px]" />
                    <Skeleton className="h-4 w-[320px]" />
                    <Skeleton className="h-4 w-[150px]" />
                </div>
            </div>
        </div>
    )
}
