"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { CalendarIcon, Check, ChevronsUpDown } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUser } from "@/providers/user-provider";

const languages = [
  { label: "English", value: "en" },
  { label: "French", value: "fr" },
  { label: "German", value: "de" },
  { label: "Spanish", value: "es" },
  { label: "Portuguese", value: "pt" },
  { label: "Russian", value: "ru" },
  { label: "Japanese", value: "ja" },
  { label: "Korean", value: "ko" },
  { label: "Chinese", value: "zh" },
] as const;

const accountFormSchema = z.object({
  username: z.string("Please enter a username").min(2).max(128),
  email: z.email("Please enter a valid email").min(2).max(128),
  language: z.string("Please select a language."),
  timezone: z.string("Please select a timezone."),
});

type AccountFormValues = z.infer<typeof accountFormSchema>;

export function AccountForm() {
  const { user } = useUser();

  const defaultValues: Partial<AccountFormValues> = {
    username: user?.username,
    email: user?.email,
    language: user?.language,
    timezone: user?.timezone,
  };
  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues,
  });

  function onSubmit(data: AccountFormValues) {
    toast("You submitted the following values:", {
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
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
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="Your username" disabled {...field} />
              </FormControl>
              <FormDescription>
                Usernames cannot be changed at this time.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="Your email" disabled {...field} />
              </FormControl>
              <FormDescription>
                Emails cannot be changed at this time.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div>
          <span className="text-xl text-foreground font-semibold">Preferences</span>
        </div>
        <FormField
          control={form.control}
          name="language"
          disabled
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Language</FormLabel>
              <Popover>
                <PopoverTrigger disabled asChild>
                  <FormControl>
                    <Button
                      variant="outline"
                      role="combobox"
                      className={cn(
                        "w-[200px] justify-between",
                        !field.value && "text-muted-foreground"
                      )}
                    >
                      {field.value
                        ? languages.find(
                            (language) => language.value === field.value
                          )?.label
                        : "Select language"}
                      <ChevronsUpDown className="opacity-50" />
                    </Button>
                  </FormControl>
                </PopoverTrigger>
                <PopoverContent className="w-[200px] p-0">
                  <Command>
                    <CommandInput placeholder="Search language..." />
                    <CommandList>
                      <CommandEmpty>No language found.</CommandEmpty>
                      <CommandGroup>
                        {languages.map((language) => (
                          <CommandItem
                            value={language.label}
                            key={language.value}
                            onSelect={() => {
                              form.setValue("language", language.value);
                            }}
                          >
                            <Check
                              className={cn(
                                "mr-2",
                                language.value === field.value
                                  ? "opacity-100"
                                  : "opacity-0"
                              )}
                            />
                            {language.label}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
              <FormDescription>
                This is the language that will be used throughout the
                application.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          name="timezone"
          disabled
          render={({ field }) => (
            <FormItem className="flex flex-col">
              <FormLabel>Timezone</FormLabel>
              <FormControl>
                <Select {...field}>
                  <SelectTrigger className="w-[280px]">
                    <SelectValue placeholder="Select a timezone" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectLabel>North America</SelectLabel>
                      <SelectItem value="est">
                        Eastern Standard Time (EST)
                      </SelectItem>
                      <SelectItem value="cst">
                        Central Standard Time (CST)
                      </SelectItem>
                      <SelectItem value="mst">
                        Mountain Standard Time (MST)
                      </SelectItem>
                      <SelectItem value="pst">
                        Pacific Standard Time (PST)
                      </SelectItem>
                      <SelectItem value="akst">
                        Alaska Standard Time (AKST)
                      </SelectItem>
                      <SelectItem value="hst">
                        Hawaii Standard Time (HST)
                      </SelectItem>
                    </SelectGroup>
                    <SelectGroup>
                      <SelectLabel>Europe & Africa</SelectLabel>
                      <SelectItem value="gmt">
                        Greenwich Mean Time (GMT)
                      </SelectItem>
                      <SelectItem value="cet">
                        Central European Time (CET)
                      </SelectItem>
                      <SelectItem value="eet">
                        Eastern European Time (EET)
                      </SelectItem>
                      <SelectItem value="west">
                        Western European Summer Time (WEST)
                      </SelectItem>
                      <SelectItem value="cat">
                        Central Africa Time (CAT)
                      </SelectItem>
                      <SelectItem value="eat">
                        East Africa Time (EAT)
                      </SelectItem>
                    </SelectGroup>
                    <SelectGroup>
                      <SelectLabel>Asia</SelectLabel>
                      <SelectItem value="msk">Moscow Time (MSK)</SelectItem>
                      <SelectItem value="ist">
                        India Standard Time (IST)
                      </SelectItem>
                      <SelectItem value="cst_china">
                        China Standard Time (CST)
                      </SelectItem>
                      <SelectItem value="jst">
                        Japan Standard Time (JST)
                      </SelectItem>
                      <SelectItem value="kst">
                        Korea Standard Time (KST)
                      </SelectItem>
                      <SelectItem value="ist_indonesia">
                        Indonesia Central Standard Time (WITA)
                      </SelectItem>
                    </SelectGroup>
                    <SelectGroup>
                      <SelectLabel>Australia & Pacific</SelectLabel>
                      <SelectItem value="awst">
                        Australian Western Standard Time (AWST)
                      </SelectItem>
                      <SelectItem value="acst">
                        Australian Central Standard Time (ACST)
                      </SelectItem>
                      <SelectItem value="aest">
                        Australian Eastern Standard Time (AEST)
                      </SelectItem>
                      <SelectItem value="nzst">
                        New Zealand Standard Time (NZST)
                      </SelectItem>
                      <SelectItem value="fjt">Fiji Time (FJT)</SelectItem>
                    </SelectGroup>
                    <SelectGroup>
                      <SelectLabel>South America</SelectLabel>
                      <SelectItem value="art">Argentina Time (ART)</SelectItem>
                      <SelectItem value="bot">Bolivia Time (BOT)</SelectItem>
                      <SelectItem value="brt">Brasilia Time (BRT)</SelectItem>
                      <SelectItem value="clt">
                        Chile Standard Time (CLT)
                      </SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </FormControl>
              <FormDescription>
                We use your timezone for all notifications.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Update account</Button>
      </form>
    </Form>
  );
}
