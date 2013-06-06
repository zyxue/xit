from distutils.core import setup

setup(name='xit',
      version='1.0',
      description='used to setup and manage multi-replica molecular dynamics simulations',
      url='http://www.zhuyixue.com',
      author='Zhuyi Xue',
      author_email='zhuyi.xue@mail.utoronto.ca',
      maintainer='Zhuyi Xue',
      maintainer_email='zhuyi.xue@mail.utoronto.ca',
      packages=['analysis_methods', 'plot_types', 'plotmp_types'],
      # py_modules=['xit'],
      py_modules=["xit", "test_xit",
                  "setupmd", "anal", "transform", "plot", "plotmp",
                  "objs", "prop", "utils", "xutils"]
      )

