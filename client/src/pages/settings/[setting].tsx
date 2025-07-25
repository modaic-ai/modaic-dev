import { ReactElement } from "react";
import { SettingsLayout } from "@/layouts/Layout";
import { useRouter } from "next/router";
import { useUser } from "@/providers/user-provider";
import withAuth from "@/providers/auth-provider";
import UserAvatar from "@/components/user/user-avatar";
import { UserType } from "@/types/user";
import { ProfileForm } from "@/components/settings/profile-form";
import { AccountForm } from "@/components/settings/account-form";
import AccessTokensTab from "@/components/settings/access-tokens";

// Types and Constants
enum SettingType {
  PROFILE = "profile",
  ACCOUNT = "account",
  NOTIFICATIONS = "notifications",
  TOKENS = "tokens",
  USAGE = "usage",
}

interface SettingsTab {
  label: string;
  redirect: string;
  type: SettingType;
}

const SETTINGS_TABS: SettingsTab[] = [
  {
    label: "Profile",
    redirect: `/settings/${SettingType.PROFILE}`,
    type: SettingType.PROFILE,
  },
  {
    label: "Account",
    redirect: `/settings/${SettingType.ACCOUNT}`,
    type: SettingType.ACCOUNT,
  },
  {
    label: "Notifications",
    redirect: `/settings/${SettingType.NOTIFICATIONS}`,
    type: SettingType.NOTIFICATIONS,
  },
  {
    label: "Access Tokens",
    redirect: `/settings/${SettingType.TOKENS}`,
    type: SettingType.TOKENS,
  },
  {
    label: "Usage",
    redirect: `/settings/${SettingType.USAGE}`,
    type: SettingType.USAGE,
  },
];

function SettingHeader({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div>
      <h2 className="text-xl font-bold tracking-tight">{title}</h2>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}

// Settings Content Components
function ProfileSetting() {
  return (
    <div className="space-y-6 max-w-2xl">
      <SettingHeader
        title="Profile Settings"
        description="Manage your account profile and preferences."
      />
      {/* Profile settings content will go here */}
      <div className="text-muted-foreground">
        <ProfileForm />
      </div>
    </div>
  );
}

function AccountSetting() {
  return (
    <div className="space-y-6 max-w-2xl">
      <SettingHeader
        title="Account Settings"
        description="Manage your account settings."
      />
      {/* Account settings content will go here */}
      <div className="text-muted-foreground">
        <AccountForm />
      </div>
    </div>
  );
}

function NotificationsSetting() {
  return (
    <div className="space-y-6">
      <SettingHeader
        title="Notifications"
        description="Configure how you receive notifications."
      />
      {/* Notifications content will go here */}
      <div className="text-muted-foreground">
        Notification settings coming soon...
      </div>
    </div>
  );
}

function TokensSetting() {
  return (
    <div className="space-y-6">
      <SettingHeader
        title="Tokens"
        description="Manage your authentication tokens."
      />
      {/* Tokens content will go here */}
      <div className="text-muted-foreground">
        <AccessTokensTab />
      </div>
    </div>
  );
}

function UsageSetting() {
  return (
    <div className="space-y-6">
      <SettingHeader
        title="Usage"
        description="Manage your usage of the service."
      />
      {/* Usage content will go here */}
      <div className="text-muted-foreground">
        Usage management coming soon...
      </div>
    </div>
  );
}

// Sidebar Components
function UserSettingsHeader({ user }: { user: UserType }) {
  return (
    <div className="px-5 py-6 flex flex-row gap-4">
      <UserAvatar userId={user.userId} dimension={70} />
      <div className="flex flex-col justify-center">
        <h1 className="text-xl font-extrabold tracking-tight text-foreground mb-1">
          {user.fullName || user.username}
        </h1>
        <p className="text-muted-foreground text-sm bg-border px-1 rounded-sm w-fit">
          {user.username}
        </p>
      </div>
    </div>
  );
}

function SettingsTabItem({
  tab,
  isActive,
  onClick,
}: {
  tab: SettingsTab;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`
        flex items-center gap-2 cursor-pointer p-2 px-5 border-t-1 
        transition-all duration-150 ease-in-out
        ${
          isActive
            ? "bg-border text-foreground"
            : "bg-transparent hover:bg-[linear-gradient(to_right,oklch(0.1715_0.0211_275.24),oklch(0.2064_0.0338_265.53))] text-muted-foreground"
        }
      `}
    >
      <span className="text-sm tracking-tight font-semibold">{tab.label}</span>
    </div>
  );
}

function SettingsSidebarContent() {
  const router = useRouter();
  const { user } = useUser();
  const currentSetting = router.query.setting as string;

  const handleTabClick = (tabRedirect: string) => {
    router.push(tabRedirect);
  };

  if (!user) {
    return null;
  }

  return (
    <div className="border w-full h-full flex flex-col overflow-hidden rounded-lg bg-[linear-gradient(to_right,oklch(0.1715_0.0211_275.24),oklch(0.2064_0.0338_265.53))]">
      <UserSettingsHeader user={user} />

      <nav className="flex-1">
        {SETTINGS_TABS.map((tab) => (
          <SettingsTabItem
            key={tab.redirect}
            tab={tab}
            isActive={currentSetting === tab.type}
            onClick={() => handleTabClick(tab.redirect)}
          />
        ))}
      </nav>
    </div>
  );
}

// Settings Content Renderer
function SettingsContentRenderer({ settingType }: { settingType: string }) {
  const settingComponents = {
    [SettingType.PROFILE]: ProfileSetting,
    [SettingType.ACCOUNT]: AccountSetting,
    [SettingType.NOTIFICATIONS]: NotificationsSetting,
    [SettingType.TOKENS]: TokensSetting,
    [SettingType.USAGE]: UsageSetting,
  };

  const SettingComponent =
    settingComponents[settingType as SettingType] || ProfileSetting;

  return <SettingComponent />;
}

// Main Settings Component
function Settings() {
  const router = useRouter();
  const { setting } = router.query;
  const settingType = (setting as string) || SettingType.PROFILE;

  return (
    <div className="p-8 py-6">
      <SettingsContentRenderer settingType={settingType} />
    </div>
  );
}

// Layout Configuration
Settings.getLayout = (page: ReactElement) => (
  <SettingsLayout
    sidebarClassName="pr-0 border-none bg-none"
    sideBarContent={<SettingsSidebarContent />}
  >
    {page}
  </SettingsLayout>
);

export default withAuth(Settings);
export { SettingsSidebarContent };
