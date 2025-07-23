import React from "react";
import Image from "next/image";
import { Skeleton } from "../ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";
import { useFetchUserById } from "@/hooks/user";

function UserAvatar({
  userId,
  className,
  deactive,
  dimension = 48,
  showTooltip,
  extraTooltipContent,
}: {
  userId?: string;
  className?: string;
  dimension?: number;
  deactive?: boolean;
  showTooltip?: boolean;
  extraTooltipContent?: React.ReactNode;
}) {
  const { data: user } = useFetchUserById(userId);

  const profilepicurl = user?.profile_picture_url;

  const imageDisplay = (
    <div
      className={cn(
        "rounded-full overflow-hidden border transition-all duration-200 ease-in-out hover:border-2 hover:border-sky-500 cursor-pointer",
        className
      )}
      style={{ width: dimension, height: dimension }}
    >
      {userId ? (
        <Image
          src={profilepicurl || `https://robohash.org/${userId}?size=300x300`}
          alt="Avatar"
          width={dimension}
          height={dimension}
          className="object-cover w-full h-full"
        />
      ) : (
        <Skeleton
          style={{ width: dimension, height: dimension }}
          className="rounded-full"
        />
      )}
    </div>
  );

  return (
    <TooltipProvider>
      <Tooltip delayDuration={300}>
        <TooltipTrigger>
          {user ? (
            imageDisplay
          ) : (
            <Skeleton
              style={{ width: dimension, height: dimension }}
              className="rounded-full"
            />
          )}
        </TooltipTrigger>
        {user && showTooltip && (
          <TooltipContent side="top" className="p-0">
            <div className="p-2 max-w-sm">
              <div className="flex items-center mb-2 mt-1">
                <div className="mr-2">{imageDisplay}</div>
                <div>
                  <div className="font-bold text-foreground truncate">
                    {user.full_name || "Anonymous"}
                  </div>
                  <div className="text-sm text-gray-400 truncate">
                    @{user.username}
                  </div>
                </div>
              </div>
              {extraTooltipContent}
            </div>
          </TooltipContent>
        )}
      </Tooltip>
    </TooltipProvider>
  );
}

export default UserAvatar;
