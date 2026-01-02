import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/Dialog'
import { Button } from '../components/ui/Button'

export function DialogDemo() {
  const [open, setOpen] = useState(false)

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button>Open Dialog</Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Radix UI Dialog Demo</DialogTitle>
            <DialogDescription>
              This is a demonstration of Radix UI Dialog accessibility features.
              It includes focus trapping, ARIA attributes, and keyboard navigation.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-gray-600">
              Try the following accessibility features:
            </p>
            <ul className="list-disc list-inside text-sm text-gray-600 mt-2 space-y-1">
              <li>Press Tab to cycle through focusable elements</li>
              <li>Press Escape to close the dialog</li>
              <li>Click outside to close the dialog</li>
              <li>Focus is trapped within the dialog</li>
              <li>Focus returns to trigger after closing</li>
            </ul>
          </div>
          <div className="flex flex-col gap-2">
            <input
              type="text"
              placeholder="First input"
              className="w-full px-3 py-2 border rounded-md"
            />
            <input
              type="text"
              placeholder="Second input"
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setOpen(false)}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
