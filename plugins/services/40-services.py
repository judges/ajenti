from plugin import PluginMaster, PluginInstance
import commands
import session
import ui
import log
import tools

class ServicesPluginMaster(PluginMaster):
	Name = 'Services'

	def OnLoad(self):
		PluginMaster.OnLoad(self)

	def MakeInstance(self):
		i = ServicesPluginInstance()
		self.Instances.append(i)
		return i


class ServicesPluginInstance(PluginInstance):
	Name = 'Services'
	_lblStat = None
	Svcs = None
	_tblSvcs = None

	def OnLoad(self, s):
		PluginInstance.OnLoad(self, s)

		c = ui.Category()
		c.Text = 'Services'
		c.Description = 'Manage initscripts'
		c.Icon = 'plug/services;icon'
		self.CategoryItem = c

		self.Svcs = Services()

		self.BuildPanel()

		log.info('ServicesPlugin', 'Started instance')


	def BuildPanel(self):
		self._lblStat = ui.Label()
		l = ui.Label('Services management')
		l.Size = 5

		c = ui.HContainer([ui.Image('plug/services;bigicon.png'), ui.Spacer(10,1), ui.VContainer([l, self._lblStat])])
		self._tblSvcs = ui.DataTable()
		self._tblSvcs.Title = 'Services'
		self._tblSvcs.Widths = [200,100,100,100]
		r = ui.DataTableRow([ui.Label('Name'), ui.Label('Status'), ui.Label('PID'), ui.Label('Control')], True)
		r.IsHeader = True
		self._tblSvcs.Rows.append(r)

		self.Panel = ui.VContainer([c, ui.Spacer(1,10), self._tblSvcs])
		return


	def HButtonClicked(self, t, e, d):
		return

	def Update(self):
		if self.Panel.Visible:
			self.Svcs.Rescan()
			self._tblSvcs.Rows = [self._tblSvcs.Rows[0]]
			cr = 0
			for e in self.Svcs.List:
				l1 = ui.Link('Start')
				l1.Tag = 'start'
				if e.Status == 'start/running':
					cr += 1
					l1.Text = 'Stop'
					l1.Tag = 'stop'
				l1.Svc = e.Name
				l1.Handler = self.HServiceClicked
				self._tblSvcs.Rows.append(ui.DataTableRow([ui.Label(e.Name), ui.Label(e.Status), ui.Label(e.PID), ui.HContainer([l1])]))
			self._lblStat.Text = str(cr) + ' running'
		return


	def HServiceClicked(self, t, e, d):
		if t.Tag == 'start':
			tools.Actions['services/start'].Run(t.Svc)
		if t.Tag == 'stop':
			tools.Actions['services/stop'].Run(t.Svc)


class Services:
	List = None

	def Rescan(self):
		ss = tools.Actions['services/list'].Run().splitlines()
		self.List = []

		for s in ss:
			a = s.split(' ')
			if a[1][0] == '(':
				a[0] += ' ' + a[1]
				a.remove(a[1])

			e = Service()
			e.Name = a[0]
			self.List.append(e)
			e.Status = a[1].strip(',')
			if e.Status == 'start/running' and len(a)>3:
				e.PID = a[3]
		self.List.sort()
		return

class Service:
	Name = ''
	Status = 'stop/waiting'
	PID = ''

	def __cmp__(self, other):
		if not self.Status == other.Status:
			return cmp(self.Status, other.Status)
		return cmp(self.Name, other.Name)



class ListAction(tools.Action):
	Name = 'list'
	Plugin = 'services'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('initctl list')

class StartAction(tools.Action):
	Name = 'start'
	Plugin = 'services'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('/etc/init.d/' + d + ' start')

class StopAction(tools.Action):
	Name = 'stop'
	Plugin = 'services'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('/etc/init.d/' + d + ' stop')

class StatusAction(tools.Action):
	Name = 'status'
	Plugin = 'services'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('initctl status ' + d)

class PureStatusAction(tools.Action):
	Name = 'status-pure'
	Plugin = 'services'

	def Run(self, d = ''):
		return tools.Actions['core/shell-run'].Run('/etc/init.d/' + d + ' status')
