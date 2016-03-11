#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`check` command for sshrc."""


import sys

import sshrc.endpoints.common


class CheckApp(sshrc.endpoints.common.App):

    def do(self):
        return self.output()


main = sshrc.endpoints.common.main(CheckApp)

if __name__ == "__main__":
    sys.exit(main())
