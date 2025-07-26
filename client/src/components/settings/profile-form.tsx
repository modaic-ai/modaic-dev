"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useUser } from "@/providers/user-provider";
import { GithubIcon, XIcon } from "@/layouts/icons";
import { Link, Linkedin } from "lucide-react";
import { useUpdateUser } from "@/hooks/user";

const optionalUrl = z
  .url("Please enter a valid URL")
  .or(z.literal(""))
  .optional();

const profileFormSchema = z.object({
  fullName: z
    .string()
    .min(2, "Name must be at least 2 characters long")
    .max(128, "Name must be at most 128 characters long")
    .optional(),
  bio: z.string("Please enter a bio").optional(),
  githubUrl: optionalUrl,
  linkedinUrl: optionalUrl,
  xUrl: optionalUrl,
  websiteUrl: optionalUrl,
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;

export function ProfileForm() {
  const { user } = useUser();
  const defaultValues: Partial<ProfileFormValues> = {
    fullName: user?.fullName,
    bio: user?.bio,
    githubUrl: user?.githubUrl,
    linkedinUrl: user?.linkedinUrl,
    xUrl: user?.xUrl,
    websiteUrl: user?.websiteUrl,
  };
  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues,
    mode: "onSubmit",
  });
  const {
    mutateAsync: updateUser,
    isPending: isUpdating,
    error,
  } = useUpdateUser();

  function onSubmit(data: ProfileFormValues) {
    updateUser({
      userId: user?.userId,
      ...data,
    });
  }

  if (!user) {
    return null;
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="fullName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>
                This is the display name on your profile.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <div>
          <div className="mb-2 text-[14px] font-medium tracking-tight leading-none">
            Avatar (optional)
          </div>
          <div>
            <div className="flex items-center w-fit">
              <Input
                className="w-[300px] cursor-pointer hover:bg-border"
                type="file"
                accept="image/*"
              />{" "}
              <Button
                type="button"
                variant={"link"}
                className="text-muted-foreground"
              >
                Remove
              </Button>
            </div>
            <div className="text-xs text-muted-foreground mt-2">
              PNG, JPG, GIF up to 10MB
            </div>
          </div>
        </div>

        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio (optional)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Tell us a little bit about yourself"
                  className="resize-none"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                You can add a short bio to describe yourself.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="githubUrl"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                <GithubIcon className="w-4 h-4" />
                GitHub (optional)
              </FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>Add your GitHub profile URL.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="linkedinUrl"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                <Linkedin size={15} />
                LinkedIn (optional)
              </FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>Add your LinkedIn profile URL.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="xUrl"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                <XIcon className="w-3 h-3" />X (Formerly Twitter) (optional)
              </FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>Add your X profile URL.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="websiteUrl"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                <Link size={15} />
                Website (optional)
              </FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>Add your website URL.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button disabled={isUpdating} type="submit">
          {isUpdating ? "Saving..." : "Save Changes"}
        </Button>
      </form>
    </Form>
  );
}
